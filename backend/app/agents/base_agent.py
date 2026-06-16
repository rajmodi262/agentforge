"""AgentForge AI — BaseAgent Class (v2: Multi-Step Reasoning)

All 7 agents inherit from this class. It handles:
- Multi-step reasoning: think → critique → refine loop
- Claude API calls (real or mock) with structured output support
- Tool-use framework (web search, calculator, etc.)
- Output validation via Pydantic models
- WebSocket event streaming (including reasoning steps)
- Error handling with retries
- Selective context extraction
"""

import json
import time
import logging
from typing import Optional, Dict, Any, List, Callable, Type
from pydantic import BaseModel, ValidationError
from app.services.claude_service import get_claude_service
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all AgentForge AI agents.
    
    Multi-step reasoning is controlled by `reasoning_steps`:
    - 1: Single-shot (backward compatible — prompt → response)
    - 3: Think → Self-Critique → Refined Output (streams each step)
    """

    name: str = "BaseAgent"
    system_prompt: str = ""
    output_schema: dict = {}
    # Pydantic model for output validation — auto-resolved from registry if None
    output_model: Optional[Type[BaseModel]] = None
    # Which previous agent keys this agent needs (empty = all)
    required_context_keys: List[str] = []
    # Tools this agent can use — list of (name, async_callable) tuples
    tools: List[tuple] = []

    # ─── Multi-step reasoning config ───
    reasoning_steps: int = 1  # 1 = single-shot, 3 = think→critique→refine
    critique_prompt: str = (
        "You just produced the analysis above. Now critically review it.\n"
        "Identify exactly 3 weaknesses, blind spots, or overly optimistic assumptions.\n"
        "For each weakness, explain WHY it's a problem and suggest a specific fix.\n"
        "Return your critique as a JSON object with keys: weaknesses (list of strings), "
        "improvements (list of strings), confidence_before (int 0-100), confidence_after (int 0-100)."
    )
    refinement_prompt: str = (
        "Given your original analysis AND the self-critique below, produce a REFINED version.\n"
        "Address every weakness identified. Be more specific, more realistic, and more actionable.\n"
        "Return the same JSON schema as your original output, but improved."
    )

    def __init__(self):
        self.claude = get_claude_service()

    async def run(
        self,
        brief: str,
        context: Dict[str, Any],
        workflow_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute this agent's task with optional multi-step reasoning."""
        start_time = time.time()
        total_tokens = 0
        total_cost = 0.0

        # Notify: agent started
        if workflow_id:
            await ws_manager.send_agent_started(workflow_id, self.name)
            step_label = "Analyzing" if self.reasoning_steps == 1 else "Step 1/3: Initial Analysis"
            await ws_manager.send_agent_thinking(
                workflow_id, self.name,
                f"{step_label} — preparing {self.name.replace(' Agent', '').lower()} analysis..."
            )

        # Run pre-processing tools (e.g., web search for research agent)
        tool_results = {}
        if self.tools:
            tool_results = await self._run_tools(brief, context, workflow_id)

        # Build the user message with filtered context + tool results
        user_message = self._build_prompt(brief, context, tool_results)

        # Resolve output model for structured generation
        model = self.output_model
        if model is None:
            try:
                from app.models.agent_outputs import AGENT_OUTPUT_MODELS
                model = AGENT_OUTPUT_MODELS.get(self.name)
            except ImportError:
                pass

        # Resolve which system prompt to use (DB-activated or class default)
        active_prompt = self._get_active_prompt()

        # ─── Step 1: Initial Analysis ───
        initial_output = await self._generate_with_retries(
            active_prompt, user_message, workflow_id, output_model=model
        )
        total_tokens += initial_output["tokens_used"]
        total_cost += initial_output["cost"]
        
        if workflow_id and initial_output.get("thought"):
            await ws_manager.send_agent_reasoning_step(
                workflow_id, self.name, 1, self.reasoning_steps,
                "Internal Reasoning",
                initial_output["thought"]
            )

        parsed_output = self._parse_output(initial_output["content"])

        if workflow_id and self.reasoning_steps > 1:
            await ws_manager.send_agent_reasoning_step(
                workflow_id, self.name, 1, self.reasoning_steps,
                "Initial Analysis",
                self._generate_preview(parsed_output)
            )

        # ─── Step 2: Self-Critique (if multi-step) ───
        critique_data = None
        if self.reasoning_steps >= 2:
            if workflow_id:
                await ws_manager.send_agent_thinking(
                    workflow_id, self.name,
                    "Step 2/3: Self-critique — identifying weaknesses and blind spots..."
                )

            critique_result = await self.claude.generate_critique(
                original_output=json.dumps(parsed_output, indent=2),
                critique_prompt=self.critique_prompt,
                agent_name=self.name,
            )
            total_tokens += critique_result["tokens_used"]
            total_cost += critique_result["cost"]

            try:
                critique_data = self._parse_output(critique_result["content"])
            except Exception:
                critique_data = {"weaknesses": [], "improvements": []}

            if workflow_id:
                weaknesses = critique_data.get("weaknesses", [])
                critique_preview = "; ".join(weaknesses[:2]) if weaknesses else "No critical issues found"
                await ws_manager.send_agent_reasoning_step(
                    workflow_id, self.name, 2, self.reasoning_steps,
                    "Self-Critique",
                    f"Found {len(weaknesses)} weaknesses: {critique_preview}"
                )

        # ─── Step 3: Refined Output (if multi-step) ───
        if self.reasoning_steps >= 3 and critique_data:
            if workflow_id:
                await ws_manager.send_agent_thinking(
                    workflow_id, self.name,
                    "Step 3/3: Refinement — producing improved analysis addressing all weaknesses..."
                )

            refinement_message = (
                f"ORIGINAL ANALYSIS:\n{json.dumps(parsed_output, indent=2)}\n\n"
                f"SELF-CRITIQUE:\n{json.dumps(critique_data, indent=2)}\n\n"
                f"{self.refinement_prompt}\n\n"
                f"Return your output as valid JSON matching this schema:\n"
                f"{json.dumps(self.output_schema, indent=2)}"
            )

            refined_result = await self._generate_with_retries(
                active_prompt, refinement_message, workflow_id, output_model=model
            )
            total_tokens += refined_result["tokens_used"]
            total_cost += refined_result["cost"]
            parsed_output = self._parse_output(refined_result["content"])

            if workflow_id:
                conf_before = critique_data.get("confidence_before", "?")
                conf_after = critique_data.get("confidence_after", "?")
                await ws_manager.send_agent_reasoning_step(
                    workflow_id, self.name, 3, self.reasoning_steps,
                    "Refined Output",
                    f"Confidence: {conf_before}% → {conf_after}% | {self._generate_preview(parsed_output)}"
                )

        # ─── Validation ───
        if model:
            try:
                validated = model(**parsed_output)
                parsed_output = validated.model_dump()
            except ValidationError as ve:
                logger.warning(f"{self.name} output validation failed: {ve}")

        execution_time = int(time.time() - start_time)

        # Notify: agent completed
        if workflow_id:
            preview = self._generate_preview(parsed_output)
            steps_info = f" ({self.reasoning_steps}-step)" if self.reasoning_steps > 1 else ""
            await ws_manager.send_agent_completed(workflow_id, self.name, f"{preview}{steps_info}")

        logger.info(
            f"{self.name} completed in {execution_time}s, {total_tokens} tokens, "
            f"{self.reasoning_steps} reasoning steps"
        )

        return {
            "output": parsed_output,
            "tokens_used": total_tokens,
            "cost": total_cost,
            "execution_time": execution_time,
        }

    async def _generate_with_retries(
        self,
        system_prompt: str,
        user_message: str,
        workflow_id: Optional[str] = None,
        output_model: Optional[Type[BaseModel]] = None,
    ) -> Dict[str, Any]:
        """Call Claude with retry logic and structured output."""
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                if output_model:
                    result = await self.claude.generate_structured(
                        system_prompt=system_prompt,
                        user_message=user_message,
                        output_model=output_model,
                        agent_name=self.name,
                        max_tokens=4096,
                    )
                else:
                    result = await self.claude.generate(
                        system_prompt=system_prompt,
                        user_message=user_message,
                        agent_name=self.name,
                        max_tokens=4096,
                    )

                # Validate structured output so malformed/invalid data triggers a
                # retry instead of silently flowing downstream. Enforced only for
                # real LLM calls — mock mode keeps its lenient behavior.
                if output_model and not self.claude.mock_mode:
                    parsed = self._parse_output(result["content"])
                    output_model(**parsed)  # raises ValidationError if invalid → retry

                return result
            except Exception as e:
                last_error = e
                logger.warning(f"{self.name} attempt {attempt + 1}/{max_retries} failed: {e}")
                if workflow_id:
                    await ws_manager.send_agent_thinking(
                        workflow_id, self.name,
                        f"Retrying... (attempt {attempt + 2}/{max_retries})"
                    )

        if workflow_id:
            await ws_manager.send_workflow_error(
                workflow_id, self.name, str(last_error)
            )
        raise RuntimeError(f"{self.name} failed after {max_retries} attempts: {last_error}")

    async def _run_tools(
        self,
        brief: str,
        context: Dict[str, Any],
        workflow_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute pre-processing tools before the main Claude call.
        Override in subclasses for agent-specific tool usage.
        """
        results = {}
        for tool_name, tool_fn in self.tools:
            try:
                if workflow_id:
                    await ws_manager.send_agent_tool_call(
                        workflow_id, self.name, tool_name,
                        f"Running {tool_name}..."
                    )
                result = await tool_fn(brief, context)
                results[tool_name] = result
                logger.info(f"{self.name} tool '{tool_name}' completed")
            except Exception as e:
                logger.warning(f"{self.name} tool '{tool_name}' failed: {e}")
                results[tool_name] = {"error": str(e)}
        return results

    def _build_prompt(
        self,
        brief: str,
        context: Dict[str, Any],
        tool_results: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build the user message with startup brief, filtered context, and tool results."""
        parts = [f"STARTUP BRIEF: {brief}"]

        # Only include context keys this agent needs
        if context:
            filtered_context = {}
            for key, value in context.items():
                if key == "brief":
                    continue
                if self.required_context_keys:
                    # Only include specified keys
                    agent_key = key.replace("_output", "")
                    if agent_key in self.required_context_keys:
                        filtered_context[key] = value
                else:
                    filtered_context[key] = value

            if filtered_context:
                parts.append("\nPREVIOUS AGENT OUTPUTS:")
                for key, value in filtered_context.items():
                    agent_label = key.replace("_output", "").replace("_", " ").title()
                    # Summarize long outputs to stay within token limits
                    value_str = json.dumps(value, indent=2)
                    if len(value_str) > 3000:
                        value_str = value_str[:3000] + "\n... [truncated for brevity]"
                    parts.append(f"\n--- {agent_label} Agent Output ---")
                    parts.append(value_str)

        # Include tool results
        if tool_results:
            parts.append("\nTOOL RESULTS (live data when available; may be labelled placeholders if a data source is not configured — do not cite placeholders as fact):")
            for tool_name, result in tool_results.items():
                parts.append(f"\n--- {tool_name} ---")
                parts.append(json.dumps(result, indent=2))

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

    def _get_active_prompt(self) -> str:
        """Check DB for an activated prompt version; fall back to class attribute.
        
        This makes the Prompt IDE actually functional — when a user activates
        a prompt version via the API, agents will use it on the next run.
        """
        try:
            from app.database import SessionLocal
            from app.models.db_models import PromptVersion

            # Map display name → registry key  (e.g. "CEO Agent" → "ceo")
            agent_key = self.name.lower().replace(" agent", "").strip()

            db = SessionLocal()
            try:
                active = db.query(PromptVersion).filter(
                    PromptVersion.agent_name == agent_key,
                    PromptVersion.is_active == True,
                ).first()
                if active and active.system_prompt:
                    return active.system_prompt
            finally:
                db.close()
        except Exception:
            pass  # DB unavailable — use class default

        return self.system_prompt


# Agent registry for MCP / Prompt IDE
AGENT_REGISTRY = {}


def _register_agent(cls):
    """Decorator-free registration — called at import time by subclasses."""
    key = cls.name.lower().replace(" agent", "").strip()
    AGENT_REGISTRY[key] = cls
    return cls
