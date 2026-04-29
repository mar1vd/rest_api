from uuid import uuid4


class BookRepository:
    def __init__(self):
        self.books = {}

    def list_books(self, skip: int, limit: int):
        books = list(self.books.values())
        return books[skip : skip + limit]

    def count_books(self):
        return len(self.books)

    def get_book(self, book_id: str):
        return self.books.get(book_id)

    def create_book(self, data: dict):
        book_id = str(uuid4())
        book = {
            "id": book_id,
            "title": data["title"],
            "author": data["author"],
            "description": data.get("description"),
            "year": data["year"],
            "status": data.get("status", "available"),
        }
        self.books[book_id] = book
        return book

    def delete_book(self, book_id: str):
        return self.books.pop(book_id, None) is not None
