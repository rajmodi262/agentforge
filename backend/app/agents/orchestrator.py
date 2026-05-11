"""StartupOS AI — Workflow Orchestrator

The heart of the system. Runs all 7 agents sequentially,
accumulates context, streams events via WebSocket, and
persists results to the database.
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.db_models import WorkflowRun, AgentTask, AgentMessage, Project
from app.services.websocket_manager import ws_manager

from app.agents.ceo_agent import CEOAgent
from app.agents.research_agent import ResearchAgent
from app.agents.marketing_agent import MarketingAgent
from app.agents.developer_agent import DeveloperAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.operations_agent import OperationsAgent

logger = logging.getLogger(__name__)

# Agent execution order — this is the core sequential pipeline
AGENT_PIPELINE = [
    ("ceo", CEOAgent),
    ("research", ResearchAgent),
    ("marketing", MarketingAgent),
    ("developer", DeveloperAgent),
    ("finance", FinanceAgent),
    ("analytics", AnalyticsAgent),
    ("operations", OperationsAgent),
]


async def run_workflow(
    workflow_id: str,
    project_id: str,
    business_idea: str,
    target_market: Optional[str] = None,
    budget_range: Optional[str] = None,
):
    """Run the full 7-agent pipeline.

    This function is called as a BackgroundTask from the API.
    It creates its own DB session and manages the full lifecycle.
    """
    db = SessionLocal()

    try:
        # Update workflow status
        workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
        workflow.status = "running"
        workflow.started_at = datetime.now(timezone.utc)
        db.commit()

        # Build the startup brief
        brief = business_idea
        if target_market:
            brief += f"\nTarget Market: {target_market}"
        if budget_range:
            brief += f"\nBudget Range: {budget_range}"

        # Context accumulates after each agent
        context = {"brief": brief}
        total_tokens = 0
        total_cost = 0.0

        # Run each agent sequentially
        for agent_key, AgentClass in AGENT_PIPELINE:
            agent = AgentClass()

            # Create agent task record
            agent_task = AgentTask(
                workflow_id=workflow_id,
                agent_name=agent.name,
                status="running",
                started_at=datetime.now(timezone.utc),
            )
            db.add(agent_task)
            db.commit()

            try:
                # Run the agent
                result = await agent.run(
                    brief=brief,
                    context=context,
                    workflow_id=workflow_id,
                )

                # Update context with this agent's output
                context[f"{agent_key}_output"] = result["output"]

                # Log inter-agent message
                if agent_key != "ceo":
                    message = AgentMessage(
                        workflow_id=workflow_id,
                        sender="CEO Agent",
                        recipient=agent.name,
                        message_type="instruction",
                        content=f"Analyze the startup brief with focus on {agent_key} aspects. Use previous agent findings for context.",
                    )
                    db.add(message)
                    await ws_manager.send_inter_agent_message(
                        workflow_id, "CEO Agent", agent.name,
                        f"Passing context to {agent.name} for analysis..."
                    )

                # Update agent task
                agent_task.status = "completed"
                agent_task.output_data = result["output"]
                agent_task.tokens_used = result["tokens_used"]
                agent_task.execution_time = result["execution_time"]
                agent_task.completed_at = datetime.now(timezone.utc)

                total_tokens += result["tokens_used"]
                total_cost += result["cost"]

                db.commit()

            except Exception as e:
                logger.error(f"Agent {agent.name} failed: {e}")
                agent_task.status = "failed"
                agent_task.completed_at = datetime.now(timezone.utc)
                db.commit()

                # Graceful degradation: continue with other agents
                await ws_manager.send_workflow_error(
                    workflow_id, agent.name, str(e)
                )
                context[f"{agent_key}_output"] = {"error": str(e)}

        # Workflow complete
        workflow.status = "completed"
        workflow.completed_at = datetime.now(timezone.utc)
        workflow.total_tokens = total_tokens
        workflow.total_cost = f"${total_cost:.4f}"
        db.commit()

        # Update project status
        project = db.query(Project).filter(Project.id == project_id).first()
        project.status = "completed"
        db.commit()

        # Notify frontend
        await ws_manager.send_workflow_completed(workflow_id)

        logger.info(f"Workflow {workflow_id} completed: {total_tokens} tokens, ${total_cost:.4f}")

    except Exception as e:
        logger.error(f"Workflow {workflow_id} failed: {e}")
        workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
        if workflow:
            workflow.status = "failed"
            workflow.error_message = str(e)
            workflow.completed_at = datetime.now(timezone.utc)
            db.commit()

        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = "error"
            db.commit()

        await ws_manager.send_workflow_error(workflow_id, "Orchestrator", str(e))

    finally:
        db.close()
