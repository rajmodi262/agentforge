"""AgentForge AI — LangGraph Workflow Engine (v2: Parallel + Board Meeting)

Production-grade multi-agent orchestrator with:
- Parallel fan-out/fan-in execution (Marketing, Developer, Finance run simultaneously)
- Board Meeting debate node (agents challenge each other before report compilation)
- Multi-step reasoning (think → critique → refine) on key agents
- Deterministic, inspectable execution flow via LangGraph StateGraph
- Full WebSocket streaming + DB persistence at each node boundary

Graph topology:

  START → CEO → Research → [Marketing, Developer, Finance] → Analytics → Operations → Board Meeting → Report → END
"""

import os
import time
import logging
from typing import TypedDict, Optional, Dict, Any, List, Annotated
from datetime import datetime, timezone
import operator

from langgraph.graph import StateGraph, START, END
from sqlalchemy.orm import Session, sessionmaker

from app.database import get_session_factory
from app.models.db_models import WorkflowRun, AgentTask, AgentMessage, Project, ProjectReport
from app.services.websocket_manager import ws_manager

from app.agents.ceo_agent import CEOAgent
from app.agents.research_agent import ResearchAgent
from app.agents.marketing_agent import MarketingAgent
from app.agents.developer_agent import DeveloperAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.operations_agent import OperationsAgent
from app.agents.report_compiler import ReportCompiler

logger = logging.getLogger(__name__)

# Ensure report output directory exists
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "generated_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


# ─────────────────────────── State Schema ───────────────────────────

def _merge_dicts(existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """Reducer: merge new keys into existing dict (non-destructive)."""
    merged = {**existing}
    merged.update(new)
    return merged


class WorkflowState(TypedDict):
    """Shared state passed through the entire LangGraph execution.
    
    Each agent node reads from this state and returns updates.
    The `agent_outputs` dict uses a custom reducer to merge results
    from each node without overwriting previous agent outputs.
    """
    # Inputs (set once at start, read-only after)
    workflow_id: str
    project_id: str
    brief: str
    target_market: Optional[str]
    budget_range: Optional[str]

    # Accumulated context — each agent appends its output
    agent_outputs: Annotated[Dict[str, Any], _merge_dicts]

    # Tracking
    completed_agents: Annotated[list, operator.add]
    total_tokens: Annotated[int, operator.add]
    total_cost: Annotated[float, operator.add]
    error_messages: Annotated[list, operator.add]

    # Report path (set by final node)
    report_path: Optional[str]

    # Injected dependencies (not serialized)
    session_factory: Optional[Any]


# ─────────────────────────── Node Functions ───────────────────────────

def _make_agent_node(agent_key: str, AgentClass):
    """Factory: creates a LangGraph node function for a given agent.
    
    Each node:
    1. Creates the agent instance
    2. Builds the context from accumulated agent_outputs
    3. Runs the agent with WebSocket streaming
    4. Persists the AgentTask to DB
    5. Returns state updates
    """

    async def node_fn(state: WorkflowState) -> dict:
        agent = AgentClass()
        workflow_id = state["workflow_id"]
        factory = state.get("session_factory") or get_session_factory()
        db: Session = factory()

        try:
            # Build context from accumulated outputs
            context = {"brief": state["brief"]}
            context.update(state.get("agent_outputs", {}))

            # Build full brief
            brief = state["brief"]
            if state.get("target_market"):
                brief += f"\nTarget Market: {state['target_market']}"
            if state.get("budget_range"):
                brief += f"\nBudget Range: {state['budget_range']}"

            # Create DB task record
            agent_task = AgentTask(
                workflow_id=workflow_id,
                agent_name=agent.name,
                status="running",
                started_at=datetime.now(timezone.utc),
            )
            db.add(agent_task)
            db.commit()

            # Send inter-agent handoff message
            completed = state.get("completed_agents", [])
            if completed:
                prev_name = completed[-1]
                msg = AgentMessage(
                    workflow_id=workflow_id,
                    sender=prev_name,
                    recipient=agent.name,
                    message_type="data",
                    content=f"Passing {prev_name} analysis to {agent.name} for cross-referencing.",
                )
                db.add(msg)
                db.commit()
                await ws_manager.send_inter_agent_message(
                    workflow_id, prev_name, agent.name,
                    f"Handing off to {agent.name}..."
                )

            # Run the agent
            result = await agent.run(
                brief=brief,
                context=context,
                workflow_id=workflow_id,
            )

            # Update DB task
            agent_task.status = "completed"
            agent_task.output_data = result["output"]
            agent_task.tokens_used = result["tokens_used"]
            agent_task.execution_time = result["execution_time"]
            agent_task.completed_at = datetime.now(timezone.utc)
            db.commit()

            # Store in RAG pipeline for future context enrichment
            try:
                from app.services.rag_service import store_agent_output
                store_agent_output(
                    project_id=state["project_id"],
                    agent_name=agent.name,
                    output=result["output"],
                    workflow_id=workflow_id,
                )
            except Exception as rag_err:
                logger.debug(f"RAG store skipped: {rag_err}")

            logger.info(f"[LangGraph] Node '{agent_key}' completed: {result['tokens_used']} tokens")

            return {
                "agent_outputs": {f"{agent_key}_output": result["output"]},
                "completed_agents": [agent.name],
                "total_tokens": result["tokens_used"],
                "total_cost": result["cost"],
            }

        except Exception as e:
            logger.error(f"[LangGraph] Node '{agent_key}' failed: {e}")
            agent_task.status = "failed"
            agent_task.completed_at = datetime.now(timezone.utc)
            db.commit()

            await ws_manager.send_workflow_error(workflow_id, agent.name, str(e))

            return {
                "agent_outputs": {f"{agent_key}_output": {"error": str(e)}},
                "completed_agents": [agent.name],
                "error_messages": [f"{agent.name}: {str(e)}"],
            }

        finally:
            db.close()

    # Set the function name for LangGraph's internal tracking
    node_fn.__name__ = f"node_{agent_key}"
    return node_fn


async def report_node(state: WorkflowState) -> dict:
    """Final node: compiles all agent outputs into a PDF report."""
    workflow_id = state["workflow_id"]
    project_id = state["project_id"]
    factory = state.get("session_factory") or get_session_factory()
    db: Session = factory()

    try:
        await ws_manager.send_agent_thinking(
            workflow_id, "Report Compiler",
            "Compiling all agent outputs into final report..."
        )

        compiler = ReportCompiler()
        context = {"brief": state["brief"]}
        context.update(state.get("agent_outputs", {}))

        report_json = compiler.compile_json(context)
        report_filename = f"AgentForge_Report_{project_id[:8]}_{int(time.time())}.pdf"
        absolute_path = os.path.join(REPORTS_DIR, report_filename)
        actual_path = compiler.generate_pdf(report_json, absolute_path)

        file_size = os.path.getsize(actual_path) if os.path.exists(actual_path) else 0
        report_record = ProjectReport(
            project_id=project_id,
            file_path=report_filename,
            file_size=file_size,
        )
        db.add(report_record)
        db.commit()

        logger.info(f"[LangGraph] Report generated: {actual_path} ({file_size} bytes)")
        return {"report_path": actual_path}

    except Exception as e:
        logger.error(f"[LangGraph] Report generation failed: {e}")
        return {"error_messages": [f"Report: {str(e)}"]}

    finally:
        db.close()


# ─────────────────────────── Graph Construction ───────────────────────────

# Agent pipeline definition
AGENT_PIPELINE = [
    ("ceo", CEOAgent),
    ("research", ResearchAgent),
    ("marketing", MarketingAgent),
    ("developer", DeveloperAgent),
    ("finance", FinanceAgent),
    ("analytics", AnalyticsAgent),
    ("operations", OperationsAgent),
]



def build_workflow_graph() -> StateGraph:
    """Construct the AgentForge 9-node LangGraph with parallel execution.
    
    Graph topology (diamond with parallel fan-out/fan-in):
    
        START → ceo → ┬─ research ──┐
                      ├─ marketing ─┤
                      ├─ developer ─┤ → analytics → operations → board_meeting → report → END
                      └─ finance ───┘
    
    - CEO runs sequentially first
    - Research, Marketing, Developer, Finance run in PARALLEL (they all consume
      CEO output but don't depend on each other)
    - Analytics waits for all 4 parallel agents to complete (fan-in)
    - Operations feeds into the Board Meeting debate
    - Board Meeting synthesizes all outputs into a consensus
    - Report compiles the final PDF
    
    The `_merge_dicts` reducer on `agent_outputs` handles concurrent writes
    safely — each agent writes to a unique key (e.g., `marketing_output`).
    """
    from app.agents.board_meeting import board_meeting_node

    graph = StateGraph(WorkflowState)

    # Add agent nodes
    for agent_key, AgentClass in AGENT_PIPELINE:
        graph.add_node(agent_key, _make_agent_node(agent_key, AgentClass))

    # Add board meeting debate node
    graph.add_node("board_meeting", board_meeting_node)

    # Add report compiler node
    graph.add_node("report", report_node)

    # ─── Edges: Sequential lead-in ───
    graph.add_edge(START, "ceo")

    # ─── Edges: Parallel fan-out (ceo → 4 agents simultaneously) ───
    graph.add_edge("ceo", "research")
    graph.add_edge("ceo", "marketing")
    graph.add_edge("ceo", "developer")
    graph.add_edge("ceo", "finance")

    # ─── Edges: Fan-in (all 4 → analytics) ───
    # Native LangGraph fan-in: analytics waits for ALL listed nodes to complete
    graph.add_edge(["research", "marketing", "developer", "finance"], "analytics")

    # ─── Edges: Sequential tail ───
    graph.add_edge("analytics", "operations")
    graph.add_edge("operations", "board_meeting")
    graph.add_edge("board_meeting", "report")
    graph.add_edge("report", END)

    return graph


# Compile once at module level — reusable across all workflow invocations
workflow_graph = build_workflow_graph().compile()


# ─────────────────────────── Entrypoint ───────────────────────────

async def run_workflow(
    workflow_id: str,
    project_id: str,
    business_idea: str,
    target_market: Optional[str] = None,
    budget_range: Optional[str] = None,
    session_factory: Optional[sessionmaker] = None,
):
    """Run the full 7-agent LangGraph pipeline.
    
    This function is called as a BackgroundTask from the API.
    It invokes the compiled LangGraph, which handles the sequential
    execution of all agent nodes + report generation.
    """
    factory = session_factory or get_session_factory()
    db: Session = factory()

    try:
        # Mark workflow as running
        workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found in database")
            return

        workflow.status = "running"
        workflow.started_at = datetime.now(timezone.utc)
        db.commit()

        # Build initial state
        initial_state: WorkflowState = {
            "workflow_id": workflow_id,
            "project_id": project_id,
            "brief": business_idea,
            "target_market": target_market,
            "budget_range": budget_range,
            "agent_outputs": {},
            "completed_agents": [],
            "total_tokens": 0,
            "total_cost": 0.0,
            "error_messages": [],
            "report_path": None,
            "session_factory": factory,
        }

        # Execute the LangGraph
        logger.info(f"[LangGraph] Starting workflow {workflow_id}")
        final_state = await workflow_graph.ainvoke(initial_state)

        # Update workflow completion
        workflow.status = "completed"
        workflow.completed_at = datetime.now(timezone.utc)
        workflow.total_tokens = final_state.get("total_tokens", 0)
        workflow.total_cost = final_state.get("total_cost", 0.0)

        if final_state.get("error_messages"):
            workflow.error_message = "; ".join(final_state["error_messages"])

        db.commit()

        # Update project status
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = "completed"
            db.commit()

        # Notify frontend
        await ws_manager.send_workflow_completed(
            workflow_id,
            project_id=project_id,
            report_available=final_state.get("report_path") is not None,
        )

        completed_count = len(final_state.get("completed_agents", []))
        logger.info(
            f"[LangGraph] Workflow {workflow_id} completed: "
            f"{final_state.get('total_tokens', 0)} tokens, "
            f"${final_state.get('total_cost', 0.0):.4f}, "
            f"{completed_count}/8 agents (incl. Board Meeting)"
        )

    except Exception as e:
        logger.error(f"[LangGraph] Workflow {workflow_id} failed: {e}", exc_info=True)
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

        await ws_manager.send_workflow_error(workflow_id, "LangGraph Orchestrator", str(e))

    finally:
        db.close()
