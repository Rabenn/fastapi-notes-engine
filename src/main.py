import json
import secrets
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

# Modelos importados para que Base los reconozca en el ciclo de vida
from src.core.config import settings
from src.core.security import create_access_token
from src.database.config import Base, engine
from src.database.redis import redis_client
from src.models.user import UserModel
from src.repositories.note import create_user_note, delete_user_note, get_user_notes
from src.repositories.user import get_user_by_email
from src.schemas.note import Note, NoteCreate
from src.schemas.user import Token, User, UserCreate, UserUpdate
from src.services.auth import (
    authenticate_user,
    get_current_admin,
    get_current_user,
    get_db,
)
from src.services.user import (
    create_user_service,
    delete_user_service,
    get_all_users_service,
    get_user_service,
    update_user_service,
)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, title="Secure Notes & Users API")

security_basic = HTTPBasic()


def verify_docs_credentials(credentials: HTTPBasicCredentials = Depends(security_basic)):
    is_user_ok = secrets.compare_digest(credentials.username, settings.DOCS_USER)
    is_pass_ok = secrets.compare_digest(credentials.password, settings.DOCS_PASS)
    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso no autorizado",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        admin_user = await get_user_by_email(session, "admin@admin.com")
        if not admin_user:
            await create_user_service(
                session,
                UserCreate(name="admin", email="admin@admin.com", password="admin"),
                is_admin=True,
            )
    yield
    await engine.dispose()
    await redis_client.aclose()


app.router.lifespan_context = lifespan

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Docs con autenticación HTTP Basic
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(_: bool = Depends(verify_docs_credentials)):
    return get_openapi(title=app.title, version="1.0.0", routes=app.routes)


@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(_: bool = Depends(verify_docs_credentials)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title=f"{app.title} - Docs")


# Autenticación JWT compatible con Swagger y Frontend
@app.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    access_token = create_access_token(data={"sub": str(user.id), "is_admin": user.is_admin})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "is_admin": user.is_admin,
    }


# Endpoints Usuarios (Acceso Administrador)
@app.get("/users/", response_model=list[User])
async def read_users(db: AsyncSession = Depends(get_db), _: UserModel = Depends(get_current_admin)):
    return await get_all_users_service(db)


@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user: UserCreate, db: AsyncSession = Depends(get_db), _: UserModel = Depends(get_current_admin)
):
    return await create_user_service(db, user)


@app.get("/users/{user_id}", response_model=User)
async def read_user(
    user_id: int, db: AsyncSession = Depends(get_db), _: UserModel = Depends(get_current_admin)
):
    return await get_user_service(db, user_id)


@app.put("/users/{user_id}", response_model=User)
async def update_user_endpoint(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    return await update_user_service(db, user_id, user)


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: int, db: AsyncSession = Depends(get_db), _: UserModel = Depends(get_current_admin)
):
    await delete_user_service(db, user_id)


# Bloc de Notas con Redis Cache-Aside
@app.get("/notes/", response_model=list[Note])
async def get_my_notes(
    db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    cache_key = f"user_notes:{current_user.id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    notes = await get_user_notes(db, current_user.id)
    notes_dict = [
        {"id": n.id, "title": n.title, "content": n.content, "user_id": n.user_id} for n in notes
    ]
    await redis_client.setex(cache_key, 60, json.dumps(notes_dict))
    return notes_dict


@app.post("/notes/", response_model=Note, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    created = await create_user_note(db, note, current_user.id)
    await redis_client.delete(f"user_notes:{current_user.id}")
    return created


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    deleted = await delete_user_note(db, note_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nota no encontrada")
    await redis_client.delete(f"user_notes:{current_user.id}")
