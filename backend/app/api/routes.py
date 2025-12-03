"""API routes"""

import asyncio
import hashlib
import logging
import time
from typing import Any

import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.config import config
from app.exceptions import ImageProxyError, ValidationError
from app.models import (
    HealthResponse,
    MerchantInfo,
    Product,
    SearchRequest,
    SearchResponse,
    ValidationRequest,
    ValidationResponse,
)
from app.scrapers import (
    AmazonScraper,
    BestBuyScraper,
    EbayScraper,
    NeweggScraper,
    TargetScraper,
    WalmartScraper,
    DuckDuckGoScraper,
)
from app.utils.database import db
from app.utils.geolocation import geolocation_service
from app.utils.price_parser import PriceParser
from app.utils.search_validator import search_validator

logger = logging.getLogger(__name__)

router = APIRouter()

# Available merchants
AVAILABLE_MERCHANTS = ["amazon", "ebay", "walmart", "target", "bestbuy", "newegg", "duckduckgo"]

# Scraper mapping
SCRAPERS = {
    "amazon": AmazonScraper,
    "ebay": EbayScraper,
    "walmart": WalmartScraper,
    "target": TargetScraper,
    "bestbuy": BestBuyScraper,
    "newegg": NeweggScraper,
    "duckduckgo": DuckDuckGoScraper,
}


def get_cache_key(query: str, merchant: str, filters: dict[str, Any]) -> str:
    """Generate cache key for search"""
    key_data = f"{query}:{merchant}:{filters!s}"
    return hashlib.sha256(key_data.encode()).hexdigest()


async def enrich_product_with_tax_shipping(
    product: Product, location: dict | None = None
) -> Product:
    """Enrich product with tax and shipping calculations"""
    if not location:
        # Try to get location (in production, would get from request IP)
        location = await geolocation_service.get_location_from_ip()

    # Calculate shipping
    shipping_cost = 0.0
    if config.is_shipping_enabled():
        shipping_cost = geolocation_service.estimate_shipping(product.merchant, product.base_price)

    # Calculate tax
    tax = 0.0
    if config.is_tax_enabled() and location:
        state = location.get("state", "")
        tax_rate = geolocation_service.get_tax_rate(state)
        tax = PriceParser.calculate_tax(product.base_price, tax_rate)

    # Calculate total
    total_price = PriceParser.calculate_total(product.base_price, shipping_cost, tax)

    # Create new product instance (Pydantic v2 models are immutable)
    return product.model_copy(
        update={
            "shipping_cost": shipping_cost,
            "tax": tax,
            "total_price": total_price,
            "price": total_price,  # Use total price as main price
        }
    )


@router.post("/api/validate", response_model=ValidationResponse)
async def validate_search(request: ValidationRequest):
    """Validate a search query and get suggestions"""
    try:
        if not request.query or not request.query.strip():
            raise ValidationError("Query cannot be empty")

        if not config.is_validation_enabled():
            # Return permissive result if validation is disabled
            # has_results=False since no actual validation was performed
            return ValidationResponse(
                is_valid=True, has_results=False, suggestions=[], confidence=0.5
            )

        result = await search_validator.validate_query(request.query)
        return ValidationResponse(**result)
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error validating query: {e}", exc_info=True)
        raise ValidationError(f"Failed to validate query: {e!s}")


@router.post("/api/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """Search for products across merchants"""
    start_time = time.time()

    # Optional pre-validation (non-blocking)
    if config.is_validation_enabled():
        try:
            validation_result = await search_validator.validate_query(request.query)
            # Log validation result but don't block search
            if not validation_result.get("is_valid", True):
                logger.warning(f"Query '{request.query}' may not return good results")
        except Exception as e:
            logger.warning(f"Validation error (non-blocking): {e}")

    # Determine which merchants to search
    merchants_to_search = request.merchants or []
    if not merchants_to_search:
        # Get enabled merchants from config
        for merchant, enabled in config.settings.get("merchants", {}).items():
            if enabled:
                merchants_to_search.append(merchant)

    all_products: list[Product] = []
    location = None

    # Check cache first
    cached_results: dict[str, list[dict[str, Any]]] = {}
    if config.is_cache_enabled():
        for merchant in merchants_to_search:
            if not config.get_merchant_enabled(merchant):
                continue
            cache_key = get_cache_key(
                request.query,
                merchant,
                {
                    "max_results": request.max_results,
                    "min_price": request.min_price,
                    "max_price": request.max_price,
                },
            )
            cached = await db.get_cached_search(cache_key)
            if cached:
                cached_results[merchant] = cached

    # Search each merchant
    tasks = []
    for merchant in merchants_to_search:
        if not config.get_merchant_enabled(merchant):
            continue

        if merchant in cached_results:
            # Use cached results
            products = [Product(**p) for p in cached_results[merchant]]
            all_products.extend(products)
            continue

        scraper_class = SCRAPERS.get(merchant)
        if not scraper_class:
            continue

        async def search_merchant(m: str, sc: type):
            try:
                async with sc() as scraper:
                    products = await scraper.search(request.query, request.max_results)
                    # Cache results
                    if config.is_cache_enabled():
                        try:
                            cache_key = get_cache_key(
                                request.query,
                                m,
                                {
                                    "max_results": request.max_results,
                                    "min_price": request.min_price,
                                    "max_price": request.max_price,
                                },
                            )
                            await db.cache_search(
                                cache_key,
                                request.query,
                                m,
                                [p.model_dump() for p in products],
                                config.get_cache_ttl_hours(),
                            )
                        except Exception as cache_error:
                            logger.warning(f"Failed to cache results for {m}: {cache_error}")
                    return products
            except Exception as e:
                logger.error(f"Error searching {m}: {e}", exc_info=True)
                # Don't fail the entire request if one merchant fails
                return []

        tasks.append(search_merchant(merchant, scraper_class))

    # Wait for all searches to complete
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                all_products.extend(result)

    # Get location for tax/shipping calculation
    location = await geolocation_service.get_location_from_ip()

    # Enrich products with tax and shipping
    enriched_products = []
    for product in all_products:
        # Apply filters
        if request.min_price is not None and product.base_price < request.min_price:
            continue
        if request.max_price is not None and product.base_price > request.max_price:
            continue
        if request.brand and request.brand.lower() not in product.title.lower():
            continue

        # Enrich with tax/shipping
        product = await enrich_product_with_tax_shipping(product, location)
        enriched_products.append(product)

    # Sort by total price
    enriched_products.sort(key=lambda p: p.total_price)

    # Handle out of stock
    in_stock = [p for p in enriched_products if p.availability != "out_of_stock"]
    out_of_stock = [p for p in enriched_products if p.availability == "out_of_stock"]

    if request.include_out_of_stock:
        final_products = in_stock + out_of_stock
    else:
        final_products = in_stock

    # Limit results
    final_products = final_products[: request.max_results]

    search_time = time.time() - start_time

    return SearchResponse(
        products=final_products,
        total_results=len(final_products),
        search_time=search_time,
        cached=len(cached_results) > 0,
        location=location,
    )


@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    merchants = []
    for merchant in AVAILABLE_MERCHANTS:
        enabled = config.get_merchant_enabled(merchant)
        version = config.version.get("scrapers", {}).get(merchant, "1.0.0")
        merchants.append(MerchantInfo(name=merchant, enabled=enabled, version=version))

    return HealthResponse(
        status="healthy", version=config.version.get("version", "0.1.0"), merchants=merchants
    )


@router.get("/api/merchants")
async def get_merchants():
    """Get list of available merchants"""
    merchants = []
    for merchant in AVAILABLE_MERCHANTS:
        merchants.append(
            {
                "name": merchant,
                "enabled": config.get_merchant_enabled(merchant),
                "version": config.version.get("scrapers", {}).get(merchant, "1.0.0"),
            }
        )
    return {"merchants": merchants}


@router.get("/api/image-proxy")
async def proxy_image(url: str):
    """Proxy images to avoid CORS issues"""
    from urllib.parse import urlparse

    # Validate URL to prevent SSRF attacks
    try:
        parsed = urlparse(url)
    except Exception:
        logger.warning(f"Invalid URL in image proxy: {url}", exc_info=True)
        raise ImageProxyError("Invalid URL format", status_code=400)

    # Only allow HTTP and HTTPS protocols
    if parsed.scheme not in ("http", "https"):
        raise ImageProxyError("Only HTTP and HTTPS URLs are allowed", status_code=400)

    # Block private/internal IP addresses and localhost
    hostname = parsed.hostname
    if not hostname:
        raise ImageProxyError("Invalid hostname", status_code=400)

    # Block localhost and private IP ranges
    blocked_hosts = {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",  # nosec
        "::1",
        "169.254.169.254",  # AWS metadata
        "metadata.google.internal",  # GCP metadata
    }

    if hostname.lower() in blocked_hosts:
        raise ImageProxyError("Access to this host is not allowed", status_code=403)

    # Block private IP ranges (10.x.x.x, 172.16-31.x.x, 192.168.x.x)
    if hostname.startswith("10.") or hostname.startswith("192.168."):
        raise ImageProxyError("Access to private IP ranges is not allowed", status_code=403)

    if hostname.startswith("172."):
        parts = hostname.split(".")
        if len(parts) >= 2:
            try:
                second_octet = int(parts[1])
                if 16 <= second_octet <= 31:
                    raise ImageProxyError(
                        "Access to private IP ranges is not allowed", status_code=403
                    )
            except ValueError:
                pass

    # Only allow known merchant image domains
    allowed_domains = {
        "amazon.com",
        "amazonaws.com",  # Amazon
        "ebay.com",
        "ebayimg.com",  # eBay
        "walmart.com",
        "walmartimages.com",  # Walmart
        "target.com",
        "targetimg1.com",  # Target
        "bestbuy.com",
        "bbystatic.com",  # Best Buy
        "newegg.com",
        "neweggimages.com",  # Newegg
    }

    # Validate hostname matches allowed domain exactly or is a proper subdomain
    hostname_lower = hostname.lower()
    is_allowed = False

    # Check exact match first
    if hostname_lower in allowed_domains:
        is_allowed = True
    else:
        # Check if it's a proper subdomain (e.g., images.amazon.com for amazon.com)
        # Must end with '.' + domain to prevent suffix matching attacks
        for domain in allowed_domains:
            if hostname_lower == domain or hostname_lower.endswith("." + domain):
                is_allowed = True
                break

    if not is_allowed:
        raise ImageProxyError("Image host not in allowed list", status_code=403)

    # Helper function to validate redirect URLs
    def validate_redirect_url(redirect_url: str) -> bool:
        """Validate that redirect URL is also safe"""
        try:
            redirect_parsed = urlparse(redirect_url)
            redirect_hostname = redirect_parsed.hostname

            if not redirect_hostname:
                return False

            # Block localhost and private IP ranges
            if redirect_hostname.lower() in blocked_hosts:
                return False

            # Block private IP ranges
            if redirect_hostname.startswith("10.") or redirect_hostname.startswith("192.168."):
                return False

            if redirect_hostname.startswith("172."):
                parts = redirect_hostname.split(".")
                if len(parts) >= 2:
                    try:
                        second_octet = int(parts[1])
                        if 16 <= second_octet <= 31:
                            return False
                    except ValueError:
                        pass

            # Validate redirect hostname matches allowed domain
            redirect_hostname_lower = redirect_hostname.lower()
            if redirect_hostname_lower in allowed_domains:
                return True

            for domain in allowed_domains:
                if redirect_hostname_lower == domain or redirect_hostname_lower.endswith(
                    "." + domain
                ):
                    return True

            return False
        except Exception:
            return False

    try:
        # Disable automatic redirects and handle them manually to validate each redirect
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            max_redirects = 5
            current_url = url
            response = None

            for _ in range(max_redirects):
                response = await client.get(current_url)

                # If not a redirect, we're done
                if response.status_code not in (301, 302, 303, 307, 308):
                    break

                # Get redirect location
                redirect_url = response.headers.get("location")
                if not redirect_url:
                    raise ImageProxyError("Invalid redirect", status_code=400)

                # Make redirect URL absolute if relative
                if not redirect_url.startswith(("http://", "https://")):
                    redirect_parsed = urlparse(current_url)
                    redirect_url = (
                        f"{redirect_parsed.scheme}://{redirect_parsed.netloc}{redirect_url}"
                    )

                # Validate redirect URL
                if not validate_redirect_url(redirect_url):
                    raise ImageProxyError("Redirect to unauthorized host", status_code=403)

                current_url = redirect_url

            if response is None:
                raise ImageProxyError("Failed to fetch image", status_code=502)

            response.raise_for_status()

            # Validate content type is an image
            content_type = response.headers.get("content-type", "").lower()
            if not content_type.startswith("image/"):
                raise ImageProxyError("URL does not point to an image", status_code=400)

            return StreamingResponse(iter([response.content]), media_type=content_type)
    except ImageProxyError:
        raise
    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP error fetching image: {e.response.status_code}")
        # Map HTTP status codes appropriately
        if e.response.status_code == 404:
            raise ImageProxyError(
                f"Image not found (HTTP {e.response.status_code})", status_code=404
            )
        elif e.response.status_code in (401, 403):
            raise ImageProxyError(f"Access denied (HTTP {e.response.status_code})", status_code=403)
        else:
            raise ImageProxyError(
                f"Failed to fetch image (HTTP {e.response.status_code})", status_code=502
            )
    except httpx.HTTPError as e:
        logger.warning(f"HTTP error fetching image: {e}")
        raise ImageProxyError("Failed to fetch image", status_code=502)
    except Exception as e:
        logger.error(f"Unexpected error in image proxy: {e}", exc_info=True)
        raise ImageProxyError("Failed to fetch image", status_code=502)
