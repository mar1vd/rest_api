from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class BookCreate(BaseModel):
    title: str
    author: str
    description: Optional[str]
    year: int
    status: str


class BookResponse(BookCreate):
    id: UUID

    class Config:
        from_attributes = True