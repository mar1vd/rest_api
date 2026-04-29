from repository.book_repository import *


def list_books(db, cursor=None, limit=10):
    books = get_books(db, cursor, limit)
    next_cursor = None

    if len(books) > limit:
        books = books[:limit]
        next_cursor = books[-1].id

    return {
        "items": books,
        "next_cursor": next_cursor,
        "limit": limit,
    }


def get_book(db, book_id):
    return get_book_by_id(db, book_id)


def create_new_book(db, data):
    return create_book(db, data)


def remove_book(db, book_id):
    return delete_book(db, book_id)
