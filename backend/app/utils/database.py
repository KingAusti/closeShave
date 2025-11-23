"""Database utilities for caching"""

import aiosqlite
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
from app.config import DATA_DIR


class Database:
    """SQLite database for caching"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (DATA_DIR / "cache.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Search cache table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS search_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    merchant TEXT NOT NULL,
                    cache_key TEXT NOT NULL UNIQUE,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            """)
            
            # Products table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    merchant TEXT NOT NULL,
                    merchant_id TEXT,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    base_price REAL NOT NULL,
                    shipping_cost REAL DEFAULT 0.0,
                    tax REAL DEFAULT 0.0,
                    total_price REAL NOT NULL,
                    image_url TEXT,
                    direct_image_url TEXT,
                    product_url TEXT NOT NULL,
                    availability TEXT DEFAULT 'in_stock',
                    brand TEXT,
                    rating REAL,
                    review_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_key ON search_cache(cache_key)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_expires ON search_cache(expires_at)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_products_merchant ON products(merchant)
            """)
            
            await db.commit()
    
    async def get_cached_search(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached search results"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT data, expires_at FROM search_cache
                WHERE cache_key = ? AND expires_at > datetime('now')
            """, (cache_key,))
            row = await cursor.fetchone()
            
            if row:
                return json.loads(row['data'])
            return None
    
    async def cache_search(self, cache_key: str, query: str, merchant: str, 
                          data: Dict[str, Any], ttl_hours: int = 1):
        """Cache search results"""
        expires_at = datetime.now() + timedelta(hours=ttl_hours)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO search_cache 
                (query, merchant, cache_key, data, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (query, merchant, cache_key, json.dumps(data), expires_at.isoformat()))
            await db.commit()
    
    async def save_product(self, product: Dict[str, Any]):
        """Save or update a product"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO products 
                (merchant, merchant_id, title, price, base_price, shipping_cost, 
                 tax, total_price, image_url, direct_image_url, product_url, 
                 availability, brand, rating, review_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                product.get('merchant'),
                product.get('merchant_id'),
                product.get('title'),
                product.get('price'),
                product.get('base_price'),
                product.get('shipping_cost', 0.0),
                product.get('tax', 0.0),
                product.get('total_price'),
                product.get('image_url'),
                product.get('direct_image_url'),
                product.get('product_url'),
                product.get('availability', 'in_stock'),
                product.get('brand'),
                product.get('rating'),
                product.get('review_count'),
            ))
            await db.commit()
    
    async def cleanup_expired(self):
        """Clean up expired cache entries"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                DELETE FROM search_cache WHERE expires_at < datetime('now')
            """)
            await db.commit()


# Global database instance
db = Database()

