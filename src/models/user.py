from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.config import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    notes = relationship("NoteModel", back_populates="user", cascade="all, delete-orphan")
