from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from enum import Enum


class BookStatus(str, Enum):
    available = "available"
    issued = "issued"


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    description: Optional[str]
    year: int = Field(..., ge=0)
    status: BookStatus = BookStatus.available


class BookResponse(BaseModel):
    id: UUID
    title: str
    author: str
    description: Optional[str]
    year: int
    status: BookStatus