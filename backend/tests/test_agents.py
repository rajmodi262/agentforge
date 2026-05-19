"""Tests for Agent system (BaseAgent, mock mode, parsing)."""

import pytest
import json
from app.agents.base_agent import BaseAgent
from app.agents.ceo_agent import CEOAgent
from app.agents.research_agent import ResearchAgent
from app.agents.marketing_agent import MarketingAgent
from app.agents.developer_agent import DeveloperAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.operations_agent import OperationsAgent


class TestBaseAgent:
    """Test BaseAgent functionality."""

    def test_parse_output_valid_json(self):
        agent = BaseAgent()
        result = agent._parse_output('{"key": "value", "number": 42}')
        assert result == {"key": "value", "number": 42}

    def test_parse_output_json_in_code_block(self):
        agent = BaseAgent()
        content = '```json\n{"key": "value"}\n```'
        result = agent._parse_output(content)
        assert result == {"key": "value"}

    def test_parse_output_json_with_surrounding_text(self):
        agent = BaseAgent()
        content = 'Here is the analysis:\n{"key": "value"}\nEnd of output.'
        result = agent._parse_output(content)
        assert result == {"key": "value"}

    def test_parse_output_invalid_json_raises(self):
        agent = BaseAgent()
        with pytest.raises(ValueError, match="Could not parse JSON"):
            agent._parse_output("This is not JSON at all")

    def test_generate_preview(self):
        agent = BaseAgent()
        output = {
            "startup_name": "TestStartup",
            "problem_statement": "A very long problem statement that describes the core issue in detail",
        }
        preview = agent._generate_preview(output)
        assert "problem_statement" in preview
        assert len(preview) < 200


class TestAgentContextKeys:
    """Test that agents declare proper context dependencies."""

    def test_ceo_agent_no_context_keys(self):
        """CEO is first — needs no previous context."""
        agent = CEOAgent()
        assert agent.required_context_keys == []

    def test_research_agent_context_keys(self):
        agent = ResearchAgent()
        assert "ceo" in agent.required_context_keys

    def test_marketing_agent_context_keys(self):
        agent = MarketingAgent()
        assert "ceo" in agent.required_context_keys
        assert "research" in agent.required_context_keys

    def test_developer_agent_context_keys(self):
        agent = DeveloperAgent()
        assert "ceo" in agent.required_context_keys

    def test_finance_agent_context_keys(self):
        agent = FinanceAgent()
        assert "ceo" in agent.required_context_keys
        assert "marketing" in agent.required_context_keys

    def test_analytics_agent_context_keys(self):
        agent = AnalyticsAgent()
        assert "marketing" in agent.required_context_keys
        assert "finance" in agent.required_context_keys

    def test_operations_agent_uses_all_context(self):
        """Operations is last — uses all previous outputs."""
        agent = OperationsAgent()
        # Operations can use all context (empty list = no filter)
        assert isinstance(agent.required_context_keys, list)


class TestAgentPromptBuilding:
    """Test prompt construction logic."""

    def test_build_prompt_with_brief_only(self):
        agent = BaseAgent()
        prompt = agent._build_prompt("Test idea", {}, None)
        assert "STARTUP BRIEF: Test idea" in prompt

    def test_build_prompt_filters_context(self):
        """Test that agents with required_context_keys only see relevant context."""
        agent = ResearchAgent()  # Only needs "ceo"
        context = {
            "ceo_output": {"startup_name": "Test"},
            "marketing_output": {"brand_name": "Should be excluded"},
        }
        prompt = agent._build_prompt("Test idea", context, None)
        assert "Ceo" in prompt
        assert "Marketing" not in prompt  # Filtered out

    def test_build_prompt_truncates_long_context(self):
        """Test that very long context values are truncated."""
        agent = BaseAgent()
        long_value = "x" * 5000
        context = {"big_output": long_value}
        prompt = agent._build_prompt("Test idea", context, None)
        assert "[truncated for brevity]" in prompt


@pytest.mark.asyncio
class TestAgentMockExecution:
    """Test agents run successfully in mock mode."""

    async def test_ceo_agent_mock(self):
        agent = CEOAgent()
        result = await agent.run(
            brief="A food delivery app for college hostels",
            context={"brief": "A food delivery app for college hostels"},
        )
        assert "output" in result
        assert "tokens_used" in result
        output = result["output"]
        assert "startup_name_suggestion" in output
        assert "problem_statement" in output

    async def test_research_agent_mock(self):
        agent = ResearchAgent()
        result = await agent.run(
            brief="A food delivery app for college hostels",
            context={
                "brief": "A food delivery app",
                "ceo_output": {"questions_for_research_agent": ["What is the market size?"]}
            },
        )
        assert "output" in result
        assert "market_size" in result["output"]

    async def test_all_agents_produce_valid_json(self):
        """Ensure all 7 agents return parseable JSON in mock mode."""
        agents = [
            CEOAgent(), ResearchAgent(), MarketingAgent(),
            DeveloperAgent(), FinanceAgent(), AnalyticsAgent(),
            OperationsAgent(),
        ]
        for agent in agents:
            result = await agent.run(
                brief="SaaS platform for HR management",
                context={"brief": "SaaS platform for HR management"},
            )
            assert isinstance(result["output"], dict), f"{agent.name} did not return dict"
            assert result["tokens_used"] > 0, f"{agent.name} reported 0 tokens"
