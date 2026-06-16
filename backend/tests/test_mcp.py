"""Tests for the MCP tool layer (app/services/mcp_server.py)."""

import pytest

from app.services.mcp_server import get_mcp_server


def test_mcp_lists_exactly_the_six_tools():
    tools = get_mcp_server().handle_list_tools()["tools"]
    names = {t["name"] for t in tools}
    assert names == {
        "agentforge_analyze",
        "agentforge_search_knowledge",
        "agentforge_get_results",
        "agentforge_list_agents",
        "agentforge_list_projects",
        "agentforge_get_metrics",
    }


def test_mcp_initialize_identity():
    info = get_mcp_server().handle_initialize()
    assert info["serverInfo"]["name"] == "agentforge-ai"
    assert "resources" in info["capabilities"]


def test_mcp_resources_have_agentforge_uris():
    resources = get_mcp_server().handle_list_resources()["resources"]
    uris = {r["uri"] for r in resources}
    assert "agentforge://agents" in uris


@pytest.mark.asyncio
async def test_mcp_search_knowledge_calls_rag(monkeypatch):
    """Regression: this tool previously called a nonexistent get_rag_service()."""
    import app.services.rag_service as rag
    monkeypatch.setattr(
        rag, "retrieve_similar_context",
        lambda **k: [{"document": "doc-alpha", "metadata": {}, "distance": 0.1}],
    )
    res = await get_mcp_server()._tool_search_knowledge({"query": "test", "n_results": 3})
    assert "doc-alpha" in res["content"][0]["text"]
