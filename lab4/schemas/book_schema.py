from pydantic import BaseModel
from typing import Optional


class BookCreate(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    year: int
    status: str = "available"


class BookResponse(BookCreate):
    id: str


class BookPage(BaseModel):
    items: list[BookResponse]
    total: int
    skip: int
    limit: int
