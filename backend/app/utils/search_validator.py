"""Search validation service using DuckDuckGo API"""

import asyncio
import logging
import time
from typing import Any

import httpx

from app.config import config

logger = logging.getLogger(__name__)


class SearchValidator:
    """Validates search terms using DuckDuckGo API"""

    def __init__(self):
        self.timeout = config.get_validation_timeout()
        self.cache_ttl_minutes = config.get_validation_cache_ttl()
        self.base_url = "https://api.duckduckgo.com"
        self.autocomplete_url = "https://duckduckgo.com/ac"
        self.rate_limiter_delay = 0.5  # Be respectful to DuckDuckGo
        # In-memory cache: {cache_key: (result_dict, timestamp)}
        self._cache: dict[str, tuple[dict[str, Any], float]] = {}

    async def validate_query(self, query: str) -> dict[str, Any]:
        """
        Validate a search query by checking if it returns results

        Returns:
            Dict with:
                - is_valid: bool
                - has_results: bool
                - suggestions: List[str]
                - confidence: float (0.0 to 1.0)
        """
        if not query or not query.strip():
            return {"is_valid": False, "has_results": False, "suggestions": [], "confidence": 0.0}

        query = query.strip()

        # Check cache first
        cache_key = f"validation:{query}"
        cached = await self._get_cached_validation(cache_key)
        if cached:
            return cached

        try:
            # Get suggestions first (faster)
            suggestions = await self._get_suggestions(query)

            # Check if query has results by trying instant answer API
            has_results = await self._check_has_results(query)

            # Determine validation status
            is_valid = has_results or len(suggestions) > 0

            # Calculate confidence based on results and suggestions
            confidence = 0.5  # Base confidence
            if has_results:
                confidence = 0.9
            elif len(suggestions) > 0:
                confidence = 0.7
            else:
                confidence = 0.2

            result = {
                "is_valid": is_valid,
                "has_results": has_results,
                "suggestions": suggestions[:5],  # Limit to 5 suggestions
                "confidence": confidence,
            }

            # Cache the result
            await self._cache_validation(cache_key, result)

            # Rate limiting
            await asyncio.sleep(self.rate_limiter_delay)

            return result

        except Exception as e:
            logger.warning(f"Error validating query '{query}': {e}")
            # Return a permissive result on error (don't block searches)
            return {
                "is_valid": True,  # Allow search even if validation fails
                "has_results": False,
                "suggestions": [],
                "confidence": 0.5,
            }

    async def _get_suggestions(self, query: str) -> list[str]:
        """Get search suggestions from DuckDuckGo autocomplete"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.autocomplete_url,
                    params={"q": query, "kl": "us-en"},
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                )
                response.raise_for_status()

                data = response.json()
                suggestions = []

                # DuckDuckGo autocomplete returns list of dicts with 'phrase' key
                for item in data:
                    if isinstance(item, dict) and "phrase" in item:
                        phrase = item["phrase"].strip()
                        if phrase and phrase.lower() != query.lower():
                            suggestions.append(phrase)
                    elif isinstance(item, str):
                        if item.strip() and item.strip().lower() != query.lower():
                            suggestions.append(item.strip())

                return suggestions[:10]  # Limit suggestions

        except Exception as e:
            logger.warning(f"Error getting suggestions for '{query}': {e}")
            return []

    async def _check_has_results(self, query: str) -> bool:
        """Check if query has results using DuckDuckGo instant answer API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/",
                    params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"},
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                )
                response.raise_for_status()

                data = response.json()

                # Check if we got meaningful results
                # DuckDuckGo returns AbstractText, Answer, or RelatedTopics
                has_abstract = bool(data.get("AbstractText"))
                has_answer = bool(data.get("Answer"))
                has_related = (
                    bool(data.get("RelatedTopics")) and len(data.get("RelatedTopics", [])) > 0
                )

                return has_abstract or has_answer or has_related

        except Exception as e:
            logger.warning(f"Error checking results for '{query}': {e}")
            return False

    async def _get_cached_validation(self, cache_key: str) -> dict[str, Any] | None:
        """Get cached validation result if it exists and is still valid"""
        if cache_key not in self._cache:
            return None

        result, timestamp = self._cache[cache_key]
        current_time = time.time()
        age_minutes = (current_time - timestamp) / 60.0

        # Check if cache entry is still valid (within TTL)
        if age_minutes < self.cache_ttl_minutes:
            return result

        # Cache entry expired, remove it
        del self._cache[cache_key]
        return None

    async def _cache_validation(self, cache_key: str, result: dict[str, Any]):
        """Cache validation result with current timestamp"""
        current_time = time.time()
        self._cache[cache_key] = (result, current_time)

        # Optional: Clean up expired entries periodically to prevent memory bloat
        # This is a simple cleanup that runs occasionally
        if len(self._cache) > 1000:  # Only clean when cache gets large
            await self._cleanup_expired_cache()

    async def _cleanup_expired_cache(self):
        """Remove expired cache entries to free memory"""
        current_time = time.time()
        expired_keys = [
            key
            for key, (_, timestamp) in self._cache.items()
            if (current_time - timestamp) / 60.0 >= self.cache_ttl_minutes
        ]
        for key in expired_keys:
            del self._cache[key]


# Global validator instance
search_validator = SearchValidator()
