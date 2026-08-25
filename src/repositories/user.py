from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from src.models.user import UserModel
from src.schemas.user import UserCreate, UserUpdate
from src.core.security import get_password_hash

async def get_all_users(db: AsyncSession):
    result = await db.execute(select(UserModel))
    return result.scalars().all()

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(UserModel).where(UserModel.email == email))
    return result.scalar_one_or_none()

async def get_user_by_identifier(db: AsyncSession, identifier: str):
    query = select(UserModel).where(or_(UserModel.name == identifier, UserModel.email == identifier))
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate, is_admin: bool = False):
    db_user = UserModel(
        name=user.name,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        is_admin=is_admin
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, user_id: int, user: UserUpdate):
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None
    if user.name is not None:
        db_user.name = user.name
    if user.email is not None:
        db_user.email = user.email
    if user.password and user.password.strip():
        db_user.hashed_password = get_password_hash(user.password)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int):
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return False
    await db.delete(db_user)
    await db.commit()
    return True