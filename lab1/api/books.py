from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import UUID

from lab1.schemas.book_schema import BookCreate, BookResponse
from lab1.services.book_service import (
    list_books,
    get_book,
    create_book,
    remove_book
)

router = APIRouter(prefix="/books")


@router.get("/", response_model=List[BookResponse])
async def get_books(
        status: Optional[str] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None
):
    return await list_books(status, author, sort_by)


@router.get("/{book_id}", response_model=BookResponse)
async def get_book_by_id(book_id: UUID):

    book = await get_book(book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@router.post("/", response_model=BookResponse, status_code=201)
async def add_book(book: BookCreate):

    new_book = await create_book(book)

    return new_book


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: UUID):

    deleted = await remove_book(book_id)

    # idempotent delete
    if not deleted:
        return

    return