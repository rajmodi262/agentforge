"""AgentForge — Real MCP Server (stdio transport).

Unlike the REST-style shim in app/services/mcp_server.py (which is driven over
HTTP via app/api/mcp.py), this is a genuine Model Context Protocol server that
speaks MCP's stdio/JSON-RPC transport. That means real MCP clients — Claude
Code, Cursor, Claude Desktop, Windsurf — can connect to it directly.

It reuses the existing tool implementations in MCPServer, so there is a single
source of truth for what each tool does.

Run:
    python -m app.mcp_stdio

Register in an MCP client (e.g. Claude Code .mcp.json):
    {
      "mcpServers": {
        "agentforge": {
          "command": "python",
          "args": ["-m", "app.mcp_stdio"],
          "cwd": "backend"
        }
      }
    }

Dependency:
    pip install "mcp[cli]"
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from app.services.mcp_server import get_mcp_server
from app.database import get_session_factory

mcp = FastMCP(
    "agentforge",
    instructions=(
        "AgentForge turns a business idea into a strategic startup blueprint "
        "using 7 specialized LLM agents (CEO, Research, Marketing, Developer, "
        "Finance, Analytics, Operations) orchestrated via LangGraph. Use these "
        "tools to start an analysis, search the knowledge base, and read results "
        "and LLMOps metrics."
    ),
)

_server = get_mcp_server()


def _text(result: dict) -> str:
    """Unwrap an MCPServer handler result into plain text for the MCP client."""
    try:
        return result["content"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return str(result)


@mcp.tool()
async def list_agents() -> str:
    """List all 7 AgentForge agents with their capabilities and tools."""
    return _text(await _server._tool_list_agents())


@mcp.tool()
async def search_knowledge(query: str, n_results: int = 5) -> str:
    """Semantic search over the AgentForge knowledge base (RAG)."""
    return _text(await _server._tool_search_knowledge({"query": query, "n_results": n_results}))


@mcp.tool()
async def list_projects(status: str = "") -> str:
    """List startup-analysis projects, optionally filtered by status."""
    db = get_session_factory()()
    try:
        args = {"status": status} if status else {}
        return _text(await _server._tool_list_projects(args, db))
    finally:
        db.close()


@mcp.tool()
async def get_results(project_id: str) -> str:
    """Get the per-agent analysis results for a project."""
    db = get_session_factory()()
    try:
        return _text(await _server._tool_get_results({"project_id": project_id}, db))
    finally:
        db.close()


@mcp.tool()
async def get_metrics(days: int = 30) -> str:
    """Get LLMOps observability metrics (calls, tokens, cost)."""
    db = get_session_factory()()
    try:
        return _text(await _server._tool_get_metrics({"days": days}, db))
    finally:
        db.close()


@mcp.tool()
async def analyze(business_idea: str, target_market: str = "", budget_range: str = "") -> str:
    """Get instructions for starting a full 7-agent analysis (runs async via the API)."""
    return _text(_server._tool_analyze_info({
        "business_idea": business_idea,
        "target_market": target_market or None,
        "budget_range": budget_range or None,
    }))


@mcp.resource("agentforge://agents")
def agents_resource() -> str:
    """Expose the agent roster as an MCP resource for client discovery."""
    return (
        "CEO, Research, Marketing, Developer, Finance, Analytics, Operations "
        "— orchestrated via LangGraph (parallel diamond topology)."
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
