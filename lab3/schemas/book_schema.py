from pydantic import BaseModel, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)


class BookPage(BaseModel):
    items: list[BookResponse]
    next_cursor: Optional[UUID] = None
    limit: int
