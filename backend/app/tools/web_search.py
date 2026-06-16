"""StartupOS AI — Web Search Tool (Brave Search API)"""

import logging
from typing import List, Dict
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3), reraise=True)
async def _execute_search(query: str, count: int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": count},
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": settings.brave_search_api_key,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()

async def web_search(query: str, count: int = 5) -> List[Dict[str, str]]:
    """Search the web using Brave Search API.

    Args:
        query: Search query string
        count: Number of results to return (max 10)

    Returns:
        List of {title, url, description} dicts
    """
    if not settings.brave_search_api_key:
        logger.warning("Brave Search API key not set, returning mock results")
        return _mock_search(query)

    try:
        data = await _execute_search(query, count)
        results = []
        for item in data.get("web", {}).get("results", [])[:count]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
            })

        logger.info(f"Brave Search: '{query}' → {len(results)} results")
        return results

    except Exception as e:
        logger.error(f"Brave Search error (after retries): {e}")
        return _mock_search(query)


def _mock_search(query: str) -> List[Dict[str, str]]:
    """Return clearly-labelled placeholder results when no Brave key is set.

    These are NOT real search results. They are explicitly marked so the LLM
    does not present them as verified facts. Set BRAVE_SEARCH_API_KEY for real data.
    """
    note = "[PLACEHOLDER — no live search configured; do not cite as fact]"
    return [
        {
            "title": f"{note} Market overview: {query}",
            "url": "https://example.com/placeholder",
            "description": (
                f"Illustrative placeholder for '{query}'. No real figures available "
                f"because BRAVE_SEARCH_API_KEY is not set. Treat market size/growth as unknown."
            ),
        },
        {
            "title": f"{note} Competitive landscape: {query}",
            "url": "https://example.com/placeholder",
            "description": (
                f"Illustrative placeholder for competitors in the '{query}' space. "
                f"Real competitor data requires a configured search provider."
            ),
        },
    ]
