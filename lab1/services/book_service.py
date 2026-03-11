from lab1.repository.book_repository import (
    get_all_books,
    get_book_by_id,
    add_book,
    delete_book
)

from uuid import uuid4
from typing import Optional


async def list_books(status=None, author=None, sort_by=None):

    books = await get_all_books()

    if status:
        books = [b for b in books if b["status"] == status]

    if author:
        books = [b for b in books if b["author"] == author]

    if sort_by == "title":
        books = sorted(books, key=lambda x: x["title"])

    if sort_by == "year":
        books = sorted(books, key=lambda x: x["year"])

    return books


async def get_book(book_id):
    return await get_book_by_id(book_id)


async def create_book(data):

    book = data.dict()

    book["id"] = uuid4()

    await add_book(book)

    return book


async def remove_book(book_id):

    deleted = await delete_book(book_id)

    return deleted