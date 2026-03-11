from lab1.models.book_model import books_db
from typing import List, Dict, Optional
from uuid import UUID


async def get_all_books() -> List[Dict]:
    return books_db


async def get_book_by_id(book_id: UUID) -> Optional[Dict]:
    for book in books_db:
        if book["id"] == book_id:
            return book
    return None


async def add_book(book: Dict):
    books_db.append(book)


async def delete_book(book_id: UUID) -> bool:
    for book in books_db:
        if book["id"] == book_id:
            books_db.remove(book)
            return True
    return False