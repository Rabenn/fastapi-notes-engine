from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.config import Base
from src.main import app
from src.schemas.user import UserCreate
from src.services.auth import get_db
from src.services.user import create_user_service

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL)
    testing_session_local = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with testing_session_local() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(
    test_db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = True
    monkeypatch.setattr("src.main.redis_client", mock_redis)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_notes_crud(client: AsyncClient, test_db_session: AsyncSession):
    await create_user_service(
        test_db_session,
        UserCreate(name="notewriter", email="notes@test.com", password="secretpassword"),
    )
    login_res = await client.post(
        "/auth/login",
        data={
            "username": "notes@test.com",
            "password": "secretpassword",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = await client.post(
        "/notes/",
        json={
            "title": "Nota de Prueba",
            "content": "Contenido de prueba",
        },
        headers=headers,
    )
    assert create_res.status_code == 201
    note_id = create_res.json()["id"]

    list_res = await client.get("/notes/", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    del_res = await client.delete(f"/notes/{note_id}", headers=headers)
    assert del_res.status_code == 204
