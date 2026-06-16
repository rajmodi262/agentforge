"""AgentForge AI — n8n Integration Service

Connects AgentForge AI to n8n's 400+ integrations via webhooks.
This gives us Slack, Gmail, Notion, Google Sheets, Airtable, 
Jira, Trello, Discord, Telegram, and hundreds more — without
building a single integration ourselves.

Architecture:
    AgentForge Agent completes → fires webhook → n8n picks up
    n8n can trigger workflows via our API → AgentForge processes

Use Cases:
    1. Post-workflow: Send results to Slack, create Notion page
    2. Trigger: GitHub issue → AgentForge analyzes the startup idea
    3. Export: Push analysis data to Google Sheets, Airtable
    4. Notify: Email/SMS/Discord when workflow completes
"""

import httpx
import logging
import json
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)


class N8nService:
    """Integration layer between AgentForge AI and n8n.
    
    n8n provides 400+ integrations via webhooks.
    We fire events → n8n routes them to any service.
    Webhooks are persisted in DB so they survive restarts.
    """

    def __init__(self):
        settings = get_settings()
        self.base_url = getattr(settings, 'n8n_base_url', None) or "http://localhost:5678"
        self.api_key = getattr(settings, 'n8n_api_key', None)
        self.enabled = bool(self.base_url and self.base_url != "http://localhost:5678")
        self._webhook_cache = None  # Lazy-loaded from DB

    @property
    def _webhooks(self) -> dict:
        """Load webhooks from DB on first access, cache in memory."""
        if self._webhook_cache is None:
            self._webhook_cache = {}
            try:
                from app.database import SessionLocal
                from app.models.db_models import N8nWebhook
                db = SessionLocal()
                try:
                    hooks = db.query(N8nWebhook).filter(N8nWebhook.is_active == True).all()
                    self._webhook_cache = {h.event_type: h.webhook_url for h in hooks}
                finally:
                    db.close()
            except Exception:
                pass  # DB not ready yet
        return self._webhook_cache

    def register_webhook(self, event_type: str, webhook_url: str):
        """Register an n8n webhook URL — persisted in DB."""
        try:
            from app.database import SessionLocal
            from app.models.db_models import N8nWebhook
            db = SessionLocal()
            try:
                existing = db.query(N8nWebhook).filter(
                    N8nWebhook.event_type == event_type
                ).first()
                if existing:
                    existing.webhook_url = webhook_url
                    existing.is_active = True
                else:
                    db.add(N8nWebhook(event_type=event_type, webhook_url=webhook_url))
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[n8n] DB persist failed: {e}")

        # Update cache
        if self._webhook_cache is None:
            self._webhook_cache = {}
        self._webhook_cache[event_type] = webhook_url
        logger.info(f"[n8n] Registered webhook for '{event_type}': {webhook_url}")

    async def fire_event(self, event_type: str, payload: dict) -> Optional[dict]:
        """Fire an event to n8n via webhook.
        
        This triggers whatever n8n workflow is connected:
        - Send to Slack channel
        - Create Notion page
        - Update Google Sheet
        - Send email notification
        - Post to Discord
        - Create Jira ticket
        - ... 400+ more integrations
        """
        webhook_url = self._webhooks.get(event_type)
        if not webhook_url:
            logger.debug(f"[n8n] No webhook registered for '{event_type}', skipping")
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook_url,
                    json={
                        "event": event_type,
                        "source": "agentforge-ai",
                        "timestamp": __import__("datetime").datetime.now(
                            __import__("datetime").timezone.utc
                        ).isoformat(),
                        "data": payload,
                    },
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "AgentForge-AI/1.0",
                    },
                )
                
                if response.status_code in (200, 201):
                    logger.info(f"[n8n] Event '{event_type}' delivered successfully")
                    try:
                        return response.json()
                    except Exception:
                        return {"status": "delivered"}
                else:
                    logger.warning(
                        f"[n8n] Webhook returned {response.status_code}: {response.text[:200]}"
                    )
                    return None

        except httpx.TimeoutException:
            logger.warning(f"[n8n] Webhook timeout for '{event_type}'")
            return None
        except Exception as e:
            logger.warning(f"[n8n] Webhook error for '{event_type}': {e}")
            return None

    # ─────────── Convenience Methods ───────────

    async def on_workflow_completed(
        self, project_id: str, project_title: str, 
        workflow_id: str, agent_results: dict,
        total_tokens: int = 0, total_cost: float = 0.0,
    ):
        """Fire when a full workflow completes.
        
        n8n can then: post to Slack, send email, create Notion doc, etc.
        """
        return await self.fire_event("workflow_completed", {
            "project_id": project_id,
            "project_title": project_title,
            "workflow_id": workflow_id,
            "agents_completed": list(agent_results.keys()),
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
            "summary": agent_results.get("ceo", {}).get("executive_summary", ""),
        })

    async def on_agent_completed(
        self, workflow_id: str, agent_name: str, 
        output_preview: str, tokens_used: int = 0,
    ):
        """Fire when an individual agent completes.
        
        n8n can then: update progress in Notion, log to Google Sheets, etc.
        """
        return await self.fire_event("agent_completed", {
            "workflow_id": workflow_id,
            "agent_name": agent_name,
            "output_preview": output_preview[:500],
            "tokens_used": tokens_used,
        })

    async def on_report_generated(
        self, project_id: str, project_title: str,
        report_path: str, file_size: int = 0,
    ):
        """Fire when a PDF report is generated.
        
        n8n can then: email the PDF, upload to Google Drive, etc.
        """
        return await self.fire_event("report_generated", {
            "project_id": project_id,
            "project_title": project_title,
            "report_path": report_path,
            "file_size_bytes": file_size,
        })

    async def on_error(
        self, workflow_id: str, agent_name: str,
        error_message: str,
    ):
        """Fire when an error occurs.
        
        n8n can then: send PagerDuty alert, post to #incidents Slack channel, etc.
        """
        return await self.fire_event("error_occurred", {
            "workflow_id": workflow_id,
            "agent_name": agent_name,
            "error_message": error_message,
        })

    def get_status(self) -> dict:
        """Get n8n integration status."""
        return {
            "enabled": self.enabled,
            "base_url": self.base_url if self.enabled else None,
            "registered_webhooks": list(self._webhooks.keys()),
            "available_events": [
                "workflow_completed",
                "agent_completed", 
                "report_generated",
                "error_occurred",
            ],
            "n8n_integrations_available": "400+",
            "examples": [
                "Slack: Post analysis results to #startup-ideas",
                "Gmail: Email PDF report to team",
                "Notion: Create analysis page in workspace",
                "Google Sheets: Log all workflow runs",
                "Discord: Notify channel on completion",
                "Jira: Create tasks from operations plan",
                "Airtable: Store competitive analysis data",
                "Telegram: Send mobile notifications",
            ],
        }


# ─────────── Singleton ───────────

_n8n_service: Optional[N8nService] = None


def get_n8n_service() -> N8nService:
    global _n8n_service
    if _n8n_service is None:
        _n8n_service = N8nService()
    return _n8n_service
