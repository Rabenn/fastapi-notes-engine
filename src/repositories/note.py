from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.note import NoteModel
from src.schemas.note import NoteCreate

async def get_user_notes(db: AsyncSession, user_id: int):
    query = select(NoteModel).where(NoteModel.user_id == user_id).order_by(NoteModel.id.desc())
    result = await db.execute(query)
    return result.scalars().all()

async def get_note_by_id(db: AsyncSession, note_id: int, user_id: int):
    query = select(NoteModel).where(NoteModel.id == note_id, NoteModel.user_id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_user_note(db: AsyncSession, note: NoteCreate, user_id: int):
    db_note = NoteModel(title=note.title, content=note.content, user_id=user_id)
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note

async def delete_user_note(db: AsyncSession, note_id: int, user_id: int):
    db_note = await get_note_by_id(db, note_id, user_id)
    if not db_note:
        return False
    await db.delete(db_note)
    await db.commit()
    return True