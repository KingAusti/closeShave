"""Search validation service using DuckDuckGo API"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any
from app.config import config


class SearchValidator:
    """Validates search terms using DuckDuckGo API"""
    
    def __init__(self):
        self.timeout = config.get_validation_timeout()
        self.cache_ttl_minutes = config.get_validation_cache_ttl()
        self.base_url = "https://api.duckduckgo.com"
        self.autocomplete_url = "https://duckduckgo.com/ac"
        self.rate_limiter_delay = 0.5  # Be respectful to DuckDuckGo
    
    async def validate_query(self, query: str) -> Dict[str, Any]:
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
            return {
                "is_valid": False,
                "has_results": False,
                "suggestions": [],
                "confidence": 0.0
            }
        
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
                "confidence": confidence
            }
            
            # Cache the result
            await self._cache_validation(cache_key, result)
            
            # Rate limiting
            await asyncio.sleep(self.rate_limiter_delay)
            
            return result
            
        except Exception as e:
            print(f"Error validating query '{query}': {e}")
            # Return a permissive result on error (don't block searches)
            return {
                "is_valid": True,  # Allow search even if validation fails
                "has_results": False,
                "suggestions": [],
                "confidence": 0.5
            }
    
    async def _get_suggestions(self, query: str) -> List[str]:
        """Get search suggestions from DuckDuckGo autocomplete"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.autocomplete_url,
                    params={"q": query, "kl": "us-en"},
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
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
            print(f"Error getting suggestions for '{query}': {e}")
            return []
    
    async def _check_has_results(self, query: str) -> bool:
        """Check if query has results using DuckDuckGo instant answer API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": "1",
                        "skip_disambig": "1"
                    },
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Check if we got meaningful results
                # DuckDuckGo returns AbstractText, Answer, or RelatedTopics
                has_abstract = bool(data.get("AbstractText"))
                has_answer = bool(data.get("Answer"))
                has_related = bool(data.get("RelatedTopics")) and len(data.get("RelatedTopics", [])) > 0
                
                return has_abstract or has_answer or has_related
                
        except Exception as e:
            print(f"Error checking results for '{query}': {e}")
            return False
    
    async def _get_cached_validation(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached validation result"""
        # Simple in-memory cache (can be enhanced with database caching later)
        # For now, rely on API rate limiting and natural caching
        return None
    
    async def _cache_validation(self, cache_key: str, result: Dict[str, Any]):
        """Cache validation result"""
        # Simple implementation - could be enhanced with database caching
        # For now, we rely on the API's natural caching and rate limiting
        pass


# Global validator instance
search_validator = SearchValidator()

