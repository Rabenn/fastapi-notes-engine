import pytest

from src.schemas.user import UserCreate
from src.services.user import create_user_service


@pytest.mark.asyncio
async def test_login_success(client, test_db_session):
    await create_user_service(
        test_db_session,
        UserCreate(name="tester", email="test@example.com", password="secretpassword")
    )

    response = await client.post("/auth/login", json={
        "username": "test@example.com",
        "password": "secretpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["name"] == "tester"

@pytest.mark.asyncio
async def test_login_invalid_password(client, test_db_session):
    await create_user_service(
        test_db_session,
        UserCreate(name="tester2", email="test2@example.com", password="secretpassword")
    )

    response = await client.post("/auth/login", json={
        "username": "test2@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
