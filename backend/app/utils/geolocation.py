"""Geolocation and tax calculation utilities"""

import logging

import httpx

from app.config import config

logger = logging.getLogger(__name__)


class GeolocationService:
    """Service for IP geolocation and tax calculation"""

    # US State sales tax rates (approximate, can be updated)
    STATE_TAX_RATES = {
        "AL": 0.04,
        "AK": 0.00,
        "AZ": 0.056,
        "AR": 0.065,
        "CA": 0.0725,
        "CO": 0.029,
        "CT": 0.0635,
        "DE": 0.00,
        "FL": 0.06,
        "GA": 0.04,
        "HI": 0.04,
        "ID": 0.06,
        "IL": 0.0625,
        "IN": 0.07,
        "IA": 0.06,
        "KS": 0.065,
        "KY": 0.06,
        "LA": 0.0445,
        "ME": 0.055,
        "MD": 0.06,
        "MA": 0.0625,
        "MI": 0.06,
        "MN": 0.06875,
        "MS": 0.07,
        "MO": 0.04225,
        "MT": 0.00,
        "NE": 0.055,
        "NV": 0.0685,
        "NH": 0.00,
        "NJ": 0.06625,
        "NM": 0.05125,
        "NY": 0.04,
        "NC": 0.0475,
        "ND": 0.05,
        "OH": 0.0575,
        "OK": 0.045,
        "OR": 0.00,
        "PA": 0.06,
        "RI": 0.07,
        "SC": 0.06,
        "SD": 0.045,
        "TN": 0.07,
        "TX": 0.0625,
        "UT": 0.061,
        "VT": 0.06,
        "VA": 0.053,
        "WA": 0.065,
        "WV": 0.06,
        "WI": 0.05,
        "WY": 0.04,
        "DC": 0.06,
    }

    def __init__(self):
        self.provider = config.get_geolocation_provider()
        self.api_key = config.get_geolocation_api_key()

    async def get_location_from_ip(self, ip: str | None = None) -> dict[str, str] | None:
        """Get location information from IP address"""
        if not ip:
            # Get client IP (would be passed from request)
            # For now, return None and use default
            return None

        try:
            if self.provider == "ip-api.com":
                url = f"http://ip-api.com/json/{ip}"
                if self.api_key:
                    url += f"?key={self.api_key}"
            else:
                # Default to ip-api.com free tier
                url = f"http://ip-api.com/json/{ip}"

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success" or "country" in data:
                        return {
                            "country": data.get("country", "US"),
                            "region": data.get("region", data.get("regionName", "")),
                            "state": data.get("regionCode", ""),
                            "city": data.get("city", ""),
                            "zip": data.get("zip", ""),
                        }
        except Exception as e:
            logger.warning(f"Error getting location from IP {ip}: {e}")

        return None

    def get_tax_rate(self, state: str | None = None) -> float:
        """Get sales tax rate for a state"""
        if not state:
            return config.settings.get("tax", {}).get("default_rate", 0.0)

        state = state.upper()
        return self.STATE_TAX_RATES.get(state, 0.0)

    def estimate_shipping(self, merchant: str, base_price: float) -> float:
        """Estimate shipping cost (simplified)"""
        if not config.is_shipping_enabled():
            return 0.0

        # Simple shipping estimates based on merchant and price
        shipping_estimates = {
            "amazon": lambda p: 0.0 if p > 25 else 5.99,  # Prime free shipping over $25
            "walmart": lambda p: 0.0 if p > 35 else 5.99,
            "target": lambda p: 0.0 if p > 35 else 5.99,
            "bestbuy": lambda p: 0.0 if p > 35 else 5.99,
            "newegg": lambda p: 0.0 if p > 50 else 7.99,
            "ebay": lambda p: 5.99,  # Varies by seller
        }

        estimate_func = shipping_estimates.get(merchant.lower(), lambda p: 5.99)
        return estimate_func(base_price)


geolocation_service = GeolocationService()
