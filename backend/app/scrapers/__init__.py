"""Scraper modules for different merchants"""

from .amazon import AmazonScraper
from .base import BaseScraper
from .bestbuy import BestBuyScraper
from .duckduckgo import DuckDuckGoScraper
from .ebay import EbayScraper
from .newegg import NeweggScraper
from .target import TargetScraper
from .walmart import WalmartScraper

__all__ = [
    "AmazonScraper",
    "BaseScraper",
    "BestBuyScraper",
    "DuckDuckGoScraper",
    "EbayScraper",
    "NeweggScraper",
    "TargetScraper",
    "WalmartScraper",
]
