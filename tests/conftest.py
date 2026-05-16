"""
pytest configuration.
Async mode set to 'auto' so all async tests work without decoration.
"""
import pytest
import pytest_asyncio
from backend.database.session import init_db
from backend.database.seed import seed_database

# Tell pytest-asyncio to handle async tests automatically
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    """Ensure the database is created and seeded before tests run."""
    await init_db()
    await seed_database()
