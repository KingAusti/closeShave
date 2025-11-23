"""API routes"""

import time
import hashlib
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import httpx

from app.models import SearchRequest, SearchResponse, Product, MerchantInfo, HealthResponse
from app.config import config
from app.scrapers import (
    AmazonScraper, EbayScraper, WalmartScraper,
    TargetScraper, BestBuyScraper, NeweggScraper
)
from app.utils.database import db
from app.utils.geolocation import geolocation_service
from app.utils.price_parser import PriceParser

router = APIRouter()

# Scraper mapping
SCRAPERS = {
    "amazon": AmazonScraper,
    "ebay": EbayScraper,
    "walmart": WalmartScraper,
    "target": TargetScraper,
    "bestbuy": BestBuyScraper,
    "newegg": NeweggScraper,
}


def get_cache_key(query: str, merchant: str, filters: dict) -> str:
    """Generate cache key for search"""
    key_data = f"{query}:{merchant}:{str(filters)}"
    return hashlib.md5(key_data.encode()).hexdigest()


async def enrich_product_with_tax_shipping(product: Product, location: Optional[dict] = None) -> Product:
    """Enrich product with tax and shipping calculations"""
    if not location:
        # Try to get location (in production, would get from request IP)
        location = await geolocation_service.get_location_from_ip()
    
    # Calculate shipping
    shipping_cost = 0.0
    if config.is_shipping_enabled():
        shipping_cost = geolocation_service.estimate_shipping(
            product.merchant, product.base_price
        )
    
    # Calculate tax
    tax = 0.0
    if config.is_tax_enabled() and location:
        state = location.get("state", "")
        tax_rate = geolocation_service.get_tax_rate(state)
        tax = PriceParser.calculate_tax(product.base_price, tax_rate)
    
    # Calculate total
    total_price = PriceParser.calculate_total(product.base_price, shipping_cost, tax)
    
    # Update product
    product.shipping_cost = shipping_cost
    product.tax = tax
    product.total_price = total_price
    product.price = total_price  # Use total price as main price
    
    return product


@router.post("/api/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """Search for products across merchants"""
    start_time = time.time()
    
    # Determine which merchants to search
    merchants_to_search = request.merchants or []
    if not merchants_to_search:
        # Get enabled merchants from config
        for merchant, enabled in config.settings.get("merchants", {}).items():
            if enabled:
                merchants_to_search.append(merchant)
    
    all_products: List[Product] = []
    location = None
    
    # Check cache first
    cached_results: Dict[str, List[Dict[str, Any]]] = {}
    if config.is_cache_enabled():
        for merchant in merchants_to_search:
            if not config.get_merchant_enabled(merchant):
                continue
            cache_key = get_cache_key(request.query, merchant, {
                "max_results": request.max_results,
                "min_price": request.min_price,
                "max_price": request.max_price,
            })
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
                        cache_key = get_cache_key(request.query, m, {
                            "max_results": request.max_results,
                        })
                        await db.cache_search(
                            cache_key, request.query, m,
                            [p.model_dump() for p in products],
                            config.get_cache_ttl_hours()
                        )
                    return products
            except Exception as e:
                print(f"Error searching {m}: {e}")
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
    final_products = final_products[:request.max_results]
    
    search_time = time.time() - start_time
    
    return SearchResponse(
        products=final_products,
        total_results=len(final_products),
        search_time=search_time,
        cached=len(cached_results) > 0,
        location=location
    )


@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    merchants = []
    for merchant in ["amazon", "ebay", "walmart", "target", "bestbuy", "newegg"]:
        enabled = config.get_merchant_enabled(merchant)
        version = config.version.get("scrapers", {}).get(merchant, "1.0.0")
        merchants.append(MerchantInfo(
            name=merchant,
            enabled=enabled,
            version=version
        ))
    
    return HealthResponse(
        status="healthy",
        version=config.version.get("version", "0.1.0"),
        merchants=merchants
    )


@router.get("/api/merchants")
async def get_merchants():
    """Get list of available merchants"""
    merchants = []
    for merchant in ["amazon", "ebay", "walmart", "target", "bestbuy", "newegg"]:
        merchants.append({
            "name": merchant,
            "enabled": config.get_merchant_enabled(merchant),
            "version": config.version.get("scrapers", {}).get(merchant, "1.0.0")
        })
    return {"merchants": merchants}


@router.get("/api/image-proxy")
async def proxy_image(url: str):
    """Proxy images to avoid CORS issues"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return StreamingResponse(
                iter([response.content]),
                media_type=response.headers.get("content-type", "image/jpeg")
            )
    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")

