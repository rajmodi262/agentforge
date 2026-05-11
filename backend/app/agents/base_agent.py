"""StartupOS AI — BaseAgent Class

All 7 agents inherit from this class. It handles:
- Claude API calls (real or mock)
- Output validation via Pydantic
- WebSocket event streaming
- Error handling with retries
"""

import json
import time
import logging
from typing import Optional, Dict, Any
from app.services.claude_service import get_claude_service
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all StartupOS AI agents."""

    name: str = "BaseAgent"
    system_prompt: str = ""
    output_schema: dict = {}

    def __init__(self):
        self.claude = get_claude_service()

    async def run(
        self,
        brief: str,
        context: Dict[str, Any],
        workflow_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute this agent's task.

        Args:
            brief: The original startup idea from the user
            context: Accumulated outputs from previous agents
            workflow_id: For WebSocket streaming (optional)

        Returns:
            Parsed JSON output from the agent
        """
        start_time = time.time()

        # Notify: agent started
        if workflow_id:
            await ws_manager.send_agent_started(workflow_id, self.name)
            await ws_manager.send_agent_thinking(
                workflow_id, self.name,
                f"Analyzing startup brief and preparing {self.name.replace(' Agent', '').lower()} analysis..."
            )

        # Build the user message with context
        user_message = self._build_prompt(brief, context)

        # Call Claude (real or mock) with retry logic
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                result = await self.claude.generate(
                    system_prompt=self.system_prompt,
                    user_message=user_message,
                    agent_name=self.name,
                    max_tokens=4096,
                )

                # Parse the JSON output
                output = self._parse_output(result["content"])

                execution_time = int(time.time() - start_time)

                # Notify: agent completed
                if workflow_id:
                    preview = self._generate_preview(output)
                    await ws_manager.send_agent_completed(workflow_id, self.name, preview)

                logger.info(f"{self.name} completed in {execution_time}s, {result['tokens_used']} tokens")

                return {
                    "output": output,
                    "tokens_used": result["tokens_used"],
                    "cost": result["cost"],
                    "execution_time": execution_time,
                }

            except Exception as e:
                last_error = e
                logger.warning(f"{self.name} attempt {attempt + 1}/{max_retries} failed: {e}")
                if workflow_id:
                    await ws_manager.send_agent_thinking(
                        workflow_id, self.name,
                        f"Retrying... (attempt {attempt + 2}/{max_retries})"
                    )

        # All retries failed
        if workflow_id:
            await ws_manager.send_workflow_error(
                workflow_id, self.name, str(last_error)
            )
        raise RuntimeError(f"{self.name} failed after {max_retries} attempts: {last_error}")

    def _build_prompt(self, brief: str, context: Dict[str, Any]) -> str:
        """Build the user message with startup brief and previous agent outputs."""
        parts = [f"STARTUP BRIEF: {brief}"]

        if context:
            parts.append("\nPREVIOUS AGENT OUTPUTS:")
            for key, value in context.items():
                if key != "brief":
                    agent_label = key.replace("_output", "").replace("_", " ").title()
                    parts.append(f"\n--- {agent_label} Agent Output ---")
                    parts.append(json.dumps(value, indent=2))

        parts.append(f"\nYOUR TASK: Produce your analysis based on the above information.")
        parts.append(f"\nReturn your output as valid JSON matching this schema:")
        parts.append(json.dumps(self.output_schema, indent=2))

        return "\n".join(parts)

    def _parse_output(self, content: str) -> Dict[str, Any]:
        """Parse the agent's response as JSON."""
        # Try direct JSON parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON from markdown code blocks
        if "```json" in content:
            start = content.index("```json") + 7
            end = content.index("```", start)
            return json.loads(content[start:end].strip())

        if "```" in content:
            start = content.index("```") + 3
            end = content.index("```", start)
            return json.loads(content[start:end].strip())

        # Try finding JSON object boundaries
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])

        raise ValueError(f"Could not parse JSON from {self.name} output")

    def _generate_preview(self, output: Dict[str, Any]) -> str:
        """Generate a short preview string for WebSocket notification."""
        # Take first 2 meaningful values from output
        preview_parts = []
        for key, value in output.items():
            if isinstance(value, str) and len(value) > 10:
                preview_parts.append(f"{key}: {value[:80]}...")
                if len(preview_parts) >= 2:
                    break
        return " | ".join(preview_parts) if preview_parts else f"{self.name} completed"
