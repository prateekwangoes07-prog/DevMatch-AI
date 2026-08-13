import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def db_session():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(
        bind=engine,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session
    await engine.dispose()
