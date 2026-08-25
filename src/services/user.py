from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user import (
    create_user,
    delete_user,
    get_all_users,
    get_user_by_email,
    get_user_by_id,
    update_user,
)
from src.schemas.user import UserCreate, UserUpdate


async def get_all_users_service(db: AsyncSession):
    return await get_all_users(db)


async def get_user_service(db: AsyncSession, user_id: int):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


async def create_user_service(db: AsyncSession, user: UserCreate, is_admin: bool = False):
    existing = await get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya está registrado"
        )
    return await create_user(db, user, is_admin=is_admin)


async def update_user_service(db: AsyncSession, user_id: int, user: UserUpdate):
    if user.email:
        existing = await get_user_by_email(db, user.email)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya está en uso"
            )
    updated = await update_user(db, user_id, user)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return updated


async def delete_user_service(db: AsyncSession, user_id: int) -> None:
    deleted = await delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
