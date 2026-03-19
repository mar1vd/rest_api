from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from core.database import SessionLocal
from schemas.book_schema import BookCreate, BookResponse
from services.book_service import *

router = APIRouter(prefix="/books")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[BookResponse])
def get_books_endpoint(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return list_books(db, skip, limit)


@router.get("/{book_id}", response_model=BookResponse)
def get_book_endpoint(book_id: UUID, db: Session = Depends(get_db)):
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(404)
    return book


@router.post("/", response_model=BookResponse, status_code=201)
def create_book_endpoint(data: BookCreate, db: Session = Depends(get_db)):
    return create_new_book(db, data)


@router.delete("/{book_id}", status_code=204)
def delete_book_endpoint(book_id: UUID, db: Session = Depends(get_db)):
    remove_book(db, book_id)