"""Web Search service integrating live search (DuckDuckGo & Tavily)."""
import logging
from typing import Optional
# pyrefly: ignore [missing-import]
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    """Service providing live web search retrieval for grounding assistant responses."""

    def __init__(self) -> None:
        self.api_key = settings.WEB_SEARCH_API_KEY.strip()

    def is_configured(self) -> bool:
        """Return True if a dedicated web search API key is set."""
        return bool(self.api_key)

    async def search(self, query: str, max_results: int = 4) -> list[dict[str, str]]:
        """
        Execute live search for query.
        Uses Tavily if API key is provided; falls back to DuckDuckGo Instant API.
        """
        cleaned_query = query.strip()
        if not cleaned_query:
            return []

        # 1. Tavily API if key is present
        if self.is_configured():
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.post(
                        "https://api.tavily.com/search",
                        json={
                            "api_key": self.api_key,
                            "query": cleaned_query,
                            "search_depth": "basic",
                            "max_results": max_results,
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        results = []
                        for item in data.get("results", []):
                            results.append(
                                {
                                    "title": item.get("title", ""),
                                    "snippet": item.get("content", ""),
                                    "url": item.get("url", ""),
                                }
                            )
                        if results:
                            return results
            except Exception as exc:
                logger.warning(f"Tavily search API failed: {exc}")

        # 2. DuckDuckGo Instant Answers API (Zero-config fallback)
        try:
            async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
                params = {"q": cleaned_query, "format": "json", "no_html": "1", "skip_disambig": "1"}
                resp = await client.get("https://api.duckduckgo.com/", params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    abstract = data.get("AbstractText", "")
                    if abstract:
                        results.append(
                            {
                                "title": data.get("Heading", "Summary"),
                                "snippet": abstract,
                                "url": data.get("AbstractURL", ""),
                            }
                        )
                    for topic in data.get("RelatedTopics", [])[:max_results]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            results.append(
                                {
                                    "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                                    "snippet": topic.get("Text", ""),
                                    "url": topic.get("FirstURL", ""),
                                }
                            )
                    if results:
                        return results
        except Exception as ddg_exc:
            logger.warning(f"DuckDuckGo search fallback failed: {ddg_exc}")

        return []

    def format_search_context(self, search_results: list[dict[str, str]]) -> str:
        """Format search results into grounded markdown context for prompt injection."""
        if not search_results:
            return ""
        snippets = []
        for i, item in enumerate(search_results, 1):
            title = item.get("title", f"Result {i}")
            snippet = item.get("snippet", "").strip()
            url = item.get("url", "")
            snippets.append(f"[Web Source {i}: {title}] ({url})\n{snippet}")
        return "\n\n".join(snippets)


search_service = SearchService()

