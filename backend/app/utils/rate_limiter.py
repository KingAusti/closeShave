"""Rate limiting and robots.txt handling"""

import asyncio
import time
from typing import Dict, Optional
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import httpx


class RateLimiter:
    """Rate limiter with robots.txt support"""
    
    def __init__(self, default_delay: float = 1.0):
        self.default_delay = default_delay
        self.last_request_time: Dict[str, float] = {}
        self.robots_parsers: Dict[str, RobotFileParser] = {}
        self.user_agent = "CloseShave-Bot/1.0"
    
    async def check_robots_txt(self, base_url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        parsed = urlparse(base_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        if domain not in self.robots_parsers:
            robots_url = f"{domain}/robots.txt"
            rp = RobotFileParser()
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(robots_url)
                    if response.status_code == 200:
                        rp.set_url(robots_url)
                        rp.read()
                    else:
                        # If robots.txt doesn't exist, create empty parser
                        # This allows all access but still caches the parser
                        pass
            except Exception:
                # If we can't fetch robots.txt, create empty parser
                # This allows all access but still caches the parser
                pass
            
            # Always cache the parser to avoid re-fetching
            self.robots_parsers[domain] = rp
        
        rp = self.robots_parsers[domain]
        return rp.can_fetch(self.user_agent, base_url)
    
    async def wait_if_needed(self, domain: str, delay: Optional[float] = None):
        """Wait if needed to respect rate limits"""
        delay = delay or self.default_delay
        now = time.time()
        
        if domain in self.last_request_time:
            time_since_last = now - self.last_request_time[domain]
            if time_since_last < delay:
                wait_time = delay - time_since_last
                await asyncio.sleep(wait_time)
        
        self.last_request_time[domain] = time.time()
    
    def set_user_agent(self, user_agent: str):
        """Set user agent for robots.txt checks"""
        self.user_agent = user_agent

