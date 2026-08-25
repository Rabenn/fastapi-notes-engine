from pydantic import BaseModel, ConfigDict

class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)