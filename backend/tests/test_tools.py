"""Tests for tools (calculator, web search)."""

import pytest
from app.tools.calculator import safe_eval
from app.tools.web_search import web_search


class TestCalculator:
    """Test the safe math evaluator."""

    def test_basic_addition(self):
        assert safe_eval("2 + 3") == 5.0

    def test_multiplication(self):
        assert safe_eval("1499 * 12") == 17988.0

    def test_percentage_calculation(self):
        result = safe_eval("1499 * 0.37")
        assert abs(result - 554.63) < 0.01

    def test_exponentiation(self):
        assert safe_eval("2 ** 10") == 1024.0

    def test_negative_numbers(self):
        assert safe_eval("-5 + 3") == -2.0

    def test_complex_expression(self):
        result = safe_eval("(100 - 30) * 12 * 500")
        assert result == 420000.0

    def test_division(self):
        assert safe_eval("100 / 4") == 25.0

    def test_division_by_zero(self):
        with pytest.raises(Exception):
            safe_eval("1 / 0")

    def test_rejects_function_calls(self):
        with pytest.raises(ValueError):
            safe_eval("__import__('os').system('ls')")

    def test_rejects_string_literals(self):
        with pytest.raises(ValueError):
            safe_eval("'hello'")

    def test_rejects_attribute_access(self):
        with pytest.raises(ValueError):
            safe_eval("().__class__.__bases__")


@pytest.mark.asyncio
class TestWebSearch:
    """Test the web search tool (mock mode)."""

    async def test_mock_search_returns_results(self):
        results = await web_search("test query", count=3)
        assert isinstance(results, list)
        assert len(results) > 0

    async def test_mock_search_has_required_fields(self):
        results = await web_search("market size India")
        for result in results:
            assert "title" in result
            assert "url" in result
            assert "description" in result

    async def test_mock_search_includes_query(self):
        results = await web_search("AI startup market")
        # Mock results should reference the query
        combined = " ".join(r["title"] + r["description"] for r in results)
        assert "AI startup market" in combined
