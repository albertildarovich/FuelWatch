"""
Общие фикстуры для тестов.
"""
from collections.abc import AsyncGenerator

import pytest
from app.database import Base, get_db
from app.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Используем SQLite в памяти для тестов — быстро и не требует PostgreSQL
TEST_DATABASE_URL = "sqlite+aiosqlite:///"


@pytest.fixture(scope="session")
def event_loop():
    """Один event loop на всю сессию"""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Один engine на всю сессию"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Каждый тест в своей транзакции, после — rollback"""
    connection = await engine.connect()
    transaction = await connection.begin()

    async_session = async_sessionmaker(
        connection, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.close()

    await transaction.rollback()
    await connection.close()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Тестовый HTTP клиент с подменой БД"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
