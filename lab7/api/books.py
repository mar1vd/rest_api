from fastapi import APIRouter, Depends, HTTPException, Query

from core.database import get_books_collection
from core.security import get_current_user
from repository.book_repository import MongoBookRepository
from schemas.book_schema import BookCreate, BookPage, BookResponse
from services.book_service import create_new_book, get_book, list_books, remove_book

router = APIRouter(prefix="/books", dependencies=[Depends(get_current_user)])


def get_book_repository(collection=Depends(get_books_collection)):
    return MongoBookRepository(collection)


@router.get("/", response_model=BookPage)
def get_books_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    repository: MongoBookRepository = Depends(get_book_repository),
):
    return list_books(repository, skip, limit)


@router.get("/{book_id}", response_model=BookResponse)
def get_book_endpoint(book_id: str, repository: MongoBookRepository = Depends(get_book_repository)):
    book = get_book(repository, book_id)
    if not book:
        raise HTTPException(404)
    return book


@router.post("/", response_model=BookResponse, status_code=201)
def create_book_endpoint(data: BookCreate, repository: MongoBookRepository = Depends(get_book_repository)):
    return create_new_book(repository, data)


@router.delete("/{book_id}", status_code=204)
def delete_book_endpoint(book_id: str, repository: MongoBookRepository = Depends(get_book_repository)):
    deleted = remove_book(repository, book_id)
    if not deleted:
        raise HTTPException(404)
