"""Pytest configuration and fixtures"""

import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient

from app.main import app
from app.utils.database import db


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator:
    """Set up test database"""
    # Initialize test database
    await db.init_db()
    yield db
    # Cleanup (if needed)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

