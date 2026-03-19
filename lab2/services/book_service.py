from repository.book_repository import *


def list_books(db, skip=0, limit=10):
    return get_books(db, skip, limit)


def get_book(db, book_id):
    return get_book_by_id(db, book_id)


def create_new_book(db, data):
    return create_book(db, data)


def remove_book(db, book_id):
    return delete_book(db, book_id)