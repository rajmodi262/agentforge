"""AgentForge AI — MCP (Model Context Protocol) Server

Implements the MCP standard so any MCP-compatible client
(Claude Desktop, Cursor, Windsurf, etc.) can interact with AgentForge.

Resources: projects, agents, knowledge docs
Tools: analyze startup, search knowledge, get results
"""

import json
import logging
from typing import Any
from app.config import get_settings

logger = logging.getLogger(__name__)


class MCPServer:
    """
    Lightweight MCP server that exposes AgentForge capabilities
    as MCP resources and tools.
    
    This follows the MCP specification (2024-11-05) with:
    - Resources: read-only data (projects, agents, docs)
    - Tools: executable actions (analyze, search, list)
    - Prompts: reusable prompt templates
    """

    def __init__(self):
        self.server_info = {
            "name": "agentforge-ai",
            "version": "1.0.0",
            "protocolVersion": "2024-11-05",
        }
        self.capabilities = {
            "resources": {"listChanged": True},
            "tools": {},
            "prompts": {},
        }
        self._tools = self._register_tools()
        self._resources = self._register_resources()
        self._prompts = self._register_prompts()

    # ─── Tool Registry ───

    def _register_tools(self) -> list[dict]:
        return [
            {
                "name": "agentforge_analyze",
                "description": "Get instructions for starting a full multi-agent startup analysis. The analysis itself runs asynchronously via the AgentForge API; this tool returns the exact endpoints and request body to kick it off and where to stream results.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "business_idea": {
                            "type": "string",
                            "description": "The startup idea to analyze (e.g., 'AI-powered meal planning app for busy professionals')",
                        },
                        "target_market": {
                            "type": "string",
                            "description": "Target market segment (optional)",
                        },
                        "budget_range": {
                            "type": "string",
                            "description": "Budget range: bootstrap/seed/series_a (optional)",
                        },
                    },
                    "required": ["business_idea"],
                },
            },
            {
                "name": "agentforge_search_knowledge",
                "description": "Search the AgentForge knowledge base using semantic/hybrid search. Returns relevant document chunks from uploaded PDFs, markdown files, and other documents.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query",
                        },
                        "n_results": {
                            "type": "integer",
                            "description": "Number of results to return (default: 5)",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "agentforge_get_results",
                "description": "Get the analysis results for a previously created project. Returns per-agent outputs including market research, financials, tech stack, and more.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "The project ID to retrieve results for",
                        },
                    },
                    "required": ["project_id"],
                },
            },
            {
                "name": "agentforge_list_agents",
                "description": "List all available AI agents in the AgentForge platform with their capabilities, tools, and current prompt versions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "agentforge_list_projects",
                "description": "List all startup analysis projects with their status (draft, running, completed).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Filter by status: draft, running, completed (optional)",
                            "enum": ["draft", "running", "completed"],
                        },
                    },
                },
            },
            {
                "name": "agentforge_get_metrics",
                "description": "Get LLMOps observability metrics: total calls, tokens, cost, latency, and error rates across all agents.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to look back (default: 30)",
                            "default": 30,
                        },
                    },
                },
            },
        ]

    # ─── Resource Registry ───

    def _register_resources(self) -> list[dict]:
        return [
            {
                "uri": "agentforge://agents",
                "name": "AgentForge Agents",
                "description": "List of all 7 specialized AI agents (CEO, Research, Marketing, Developer, Finance, Analytics, Operations)",
                "mimeType": "application/json",
            },
            {
                "uri": "agentforge://knowledge",
                "name": "Knowledge Base",
                "description": "Uploaded documents and their metadata for RAG-powered agent context",
                "mimeType": "application/json",
            },
            {
                "uri": "agentforge://metrics",
                "name": "Platform Metrics",
                "description": "Aggregate LLMOps metrics (tokens, cost, latency, error rates)",
                "mimeType": "application/json",
            },
        ]

    # ─── Prompt Registry ───

    def _register_prompts(self) -> list[dict]:
        return [
            {
                "name": "startup_analysis",
                "description": "Analyze a startup idea with 7 specialized AI agents",
                "arguments": [
                    {"name": "business_idea", "description": "The startup idea to analyze", "required": True},
                    {"name": "target_market", "description": "Target market segment", "required": False},
                ],
            },
            {
                "name": "knowledge_query",
                "description": "Search the knowledge base for relevant information",
                "arguments": [
                    {"name": "query", "description": "Search query", "required": True},
                ],
            },
        ]

    # ─── Protocol Handlers ───

    def handle_initialize(self) -> dict:
        """Handle MCP initialize request."""
        return {
            "protocolVersion": self.server_info["protocolVersion"],
            "serverInfo": {
                "name": self.server_info["name"],
                "version": self.server_info["version"],
            },
            "capabilities": self.capabilities,
        }

    def handle_list_tools(self) -> dict:
        """Handle tools/list request."""
        return {"tools": self._tools}

    def handle_list_resources(self) -> dict:
        """Handle resources/list request."""
        return {"resources": self._resources}

    def handle_list_prompts(self) -> dict:
        """Handle prompts/list request."""
        return {"prompts": self._prompts}

    async def handle_call_tool(self, name: str, arguments: dict, db_session=None) -> dict:
        """Handle tools/call request — execute the requested tool."""
        try:
            if name == "agentforge_list_agents":
                return await self._tool_list_agents()
            elif name == "agentforge_search_knowledge":
                return await self._tool_search_knowledge(arguments)
            elif name == "agentforge_get_metrics":
                return await self._tool_get_metrics(arguments, db_session)
            elif name == "agentforge_list_projects":
                return await self._tool_list_projects(arguments, db_session)
            elif name == "agentforge_get_results":
                return await self._tool_get_results(arguments, db_session)
            elif name == "agentforge_analyze":
                return self._tool_analyze_info(arguments)
            else:
                return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}
        except Exception as e:
            logger.error(f"MCP tool error ({name}): {e}")
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}

    # ─── Tool Implementations ───

    async def _tool_list_agents(self) -> dict:
        from app.agents.base_agent import AGENT_REGISTRY
        agents = []
        for key, cls in AGENT_REGISTRY.items():
            agents.append({
                "name": cls.display_name if hasattr(cls, 'display_name') else key,
                "key": key,
                "description": cls.__doc__ or "",
                "tools": [t.__name__ if hasattr(t, '__name__') else str(t) for t in (cls.tools if hasattr(cls, 'tools') else [])],
            })
        return {"content": [{"type": "text", "text": json.dumps(agents, indent=2)}]}

    async def _tool_search_knowledge(self, args: dict) -> dict:
        from app.services.rag_service import retrieve_similar_context
        results = retrieve_similar_context(
            query=args["query"],
            n_results=args.get("n_results", 5),
        )
        return {"content": [{"type": "text", "text": json.dumps(results, indent=2, default=str)}]}

    async def _tool_get_metrics(self, args: dict, db) -> dict:
        if not db:
            return {"content": [{"type": "text", "text": "Database session required"}], "isError": True}
        from sqlalchemy import func
        from app.models.db_models import AgentLog
        days = args.get("days", 30)
        logs = db.query(AgentLog).limit(100).all()
        total_tokens = sum(l.total_tokens or 0 for l in logs)
        total_cost = sum(l.cost_usd or 0 for l in logs)
        result = {
            "total_calls": len(logs),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
        }
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    async def _tool_list_projects(self, args: dict, db) -> dict:
        if not db:
            return {"content": [{"type": "text", "text": "Database session required"}], "isError": True}
        from app.models.db_models import Project
        query = db.query(Project)
        if args.get("status"):
            query = query.filter(Project.status == args["status"])
        projects = query.order_by(Project.created_at.desc()).limit(20).all()
        result = [{"id": str(p.id), "title": p.title, "status": p.status} for p in projects]
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    async def _tool_get_results(self, args: dict, db) -> dict:
        if not db:
            return {"content": [{"type": "text", "text": "Database session required"}], "isError": True}
        from app.services.database_service import DatabaseService
        db_svc = DatabaseService(db)
        results = db_svc.get_project_results(args["project_id"])
        return {"content": [{"type": "text", "text": json.dumps(results, indent=2, default=str)}]}

    def _tool_analyze_info(self, args: dict) -> dict:
        """Returns instructions for running an analysis (async operation)."""
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "message": "To run a startup analysis, use the AgentForge API:",
                    "endpoint": "POST /api/v1/projects/",
                    "body": {
                        "title": args.get("business_idea", "")[:50],
                        "business_idea": args["business_idea"],
                        "target_market": args.get("target_market"),
                        "budget_range": args.get("budget_range"),
                    },
                    "then": "POST /api/v1/projects/{project_id}/start to begin the 7-agent analysis",
                    "note": "The analysis runs asynchronously via WebSocket. Connect to /ws/{workflow_id} for real-time updates.",
                }, indent=2),
            }],
        }


# ─── Singleton ───

_mcp_server: MCPServer | None = None


def get_mcp_server() -> MCPServer:
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
    return _mcp_server
