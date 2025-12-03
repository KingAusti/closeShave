"""DuckDuckGo scraper"""

import logging
from duckduckgo_search import DDGS

from app.models import Product
from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class DuckDuckGoScraper(BaseScraper):
    """Scraper for DuckDuckGo deals"""

    def __init__(self):
        # Pass "duckduckgo" as merchant name, though we don't use much config for it
        super().__init__("duckduckgo")
        self.ddgs = DDGS()

    async def search(self, query: str, max_results: int = 20) -> list[Product]:
        """Search for products using DuckDuckGo"""
        results = []
        try:
            # Search for deals
            # We append "deal price" to try to find product pages or deal listings
            search_query = f"{query} deal price"
            
            # Use text search as it's the most reliable entry point
            # In a real scenario, we might want to use 'shopping' if available and reliable
            ddg_results = self.ddgs.text(search_query, max_results=max_results)
            
            for r in ddg_results:
                title = r.get("title", "")
                link = r.get("href", "")
                body = r.get("body", "")
                
                # Try to extract price from title or body
                # This is a best-effort extraction since DDG text results don't have structured price
                price = self.price_parser.parse_price(title)
                if not price:
                    price = self.price_parser.parse_price(body)
                
                # If no price found, we might skip or set to 0. 
                # For a "deal" search, showing items without price might be less useful,
                # but let's include them if they look relevant, or maybe default to 0.
                # However, Product model requires price.
                if not price:
                    # Try to find a dollar sign in the text
                    if "$" in title or "$" in body:
                        # Maybe the parser missed it?
                        pass
                    else:
                        continue

                product = Product(
                    title=title,
                    price=price,
                    base_price=price,
                    total_price=price,
                    image_url="",  # DDG text search doesn't provide images
                    direct_image_url="",
                    product_url=link,
                    merchant="duckduckgo",
                    availability="in_stock",
                    brand=None,
                    rating=None,
                    review_count=None
                )
                results.append(product)
                
        except Exception as e:
            logger.error(f"Error searching DuckDuckGo: {e}", exc_info=True)
            
        return results

    def _parse_results(self, soup, max_results):
        """Not used for DuckDuckGo"""
        return []
