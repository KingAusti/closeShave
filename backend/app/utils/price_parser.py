"""Price parsing and normalization utilities"""

import re


class PriceParser:
    """Parse and normalize prices from various formats"""

    @staticmethod
    def parse_price(price_text: str) -> float | None:
        """
        Parse price from text string.
        Handles formats like: $19.99, 19.99, $1,234.56, etc.
        """
        if not price_text:
            return None

        # Remove common currency symbols and whitespace
        price_text = price_text.strip().replace(",", "")

        # Extract number (including decimal)
        # Matches: $19.99, 19.99, $1,234.56, etc.
        match = re.search(r"(\d+\.?\d*)", price_text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None

        return None

    @staticmethod
    def normalize_price(price: float) -> float:
        """Normalize price to 2 decimal places"""
        return round(price, 2)

    @staticmethod
    def format_price(price: float) -> str:
        """Format price as currency string"""
        return f"${price:.2f}"

    @staticmethod
    def calculate_total(base_price: float, shipping: float = 0.0, tax: float = 0.0) -> float:
        """Calculate total price including shipping and tax"""
        total = base_price + shipping + tax
        return PriceParser.normalize_price(total)

    @staticmethod
    def calculate_tax(base_price: float, tax_rate: float) -> float:
        """Calculate tax amount"""
        tax = base_price * tax_rate
        return PriceParser.normalize_price(tax)
