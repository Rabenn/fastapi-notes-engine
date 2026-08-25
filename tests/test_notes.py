import pytest

from src.schemas.user import UserCreate
from src.services.user import create_user_service


@pytest.mark.asyncio
async def test_notes_crud(client, test_db_session):
    # Registrar usuario y obtener JWT
    await create_user_service(
        test_db_session,
        UserCreate(name="notewriter", email="notes@test.com", password="secretpassword")
    )
    login_res = await client.post("/auth/login", json={
        "username": "notes@test.com",
        "password": "secretpassword"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Crear Nota
    create_res = await client.post("/notes/", json={
        "title": "Nota de Prueba",
        "content": "Contenido de prueba"
    }, headers=headers)
    assert create_res.status_code == 201
    note_id = create_res.json()["id"]

    # 2. Leer Notas
    list_res = await client.get("/notes/", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 3. Borrar Nota
    del_res = await client.delete(f"/notes/{note_id}", headers=headers)
    assert del_res.status_code == 204
