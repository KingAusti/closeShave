"""Scraper modules for different merchants"""

from .base import BaseScraper
from .amazon import AmazonScraper
from .ebay import EbayScraper
from .walmart import WalmartScraper
from .target import TargetScraper
from .bestbuy import BestBuyScraper
from .newegg import NeweggScraper

__all__ = [
    "BaseScraper",
    "AmazonScraper",
    "EbayScraper",
    "WalmartScraper",
    "TargetScraper",
    "BestBuyScraper",
    "NeweggScraper",
]

