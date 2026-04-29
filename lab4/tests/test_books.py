import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from api.books import get_book_repository
from main import app


class InMemoryBookRepository:
    def __init__(self):
        self.books = []

    def get_books(self, skip: int, limit: int):
        return self.books[skip : skip + limit]

    def count_books(self):
        return len(self.books)

    def get_book_by_id(self, book_id: str):
        return next((book for book in self.books if book["id"] == book_id), None)

    def create_book(self, data):
        book = {
            "id": str(ObjectId()),
            **data.model_dump(),
        }
        self.books.append(book)
        return book

    def delete_book(self, book_id: str):
        book = self.get_book_by_id(book_id)
        if not book:
            return False
        self.books.remove(book)
        return True


repository = InMemoryBookRepository()


def override_book_repository():
    return repository


app.dependency_overrides[get_book_repository] = override_book_repository
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_repository():
    repository.books.clear()


def create_book(title: str):
    return client.post(
        "/books/",
        json={
            "title": title,
            "author": "Me",
            "description": "Test",
            "year": 2026,
            "status": "available",
        },
    )


def test_create_book():
    res = create_book("Test")

    assert res.status_code == 201
    payload = res.json()
    assert payload["id"]
    assert payload["title"] == "Test"


def test_get_books_uses_limit_offset_pagination():
    for title in ["First", "Second", "Third"]:
        assert create_book(title).status_code == 201

    first_page = client.get("/books/", params={"skip": 0, "limit": 2})

    assert first_page.status_code == 200
    first_payload = first_page.json()
    assert first_payload["total"] == 3
    assert first_payload["skip"] == 0
    assert first_payload["limit"] == 2
    assert [book["title"] for book in first_payload["items"]] == ["First", "Second"]

    second_page = client.get("/books/", params={"skip": 2, "limit": 2})

    assert second_page.status_code == 200
    second_payload = second_page.json()
    assert second_payload["total"] == 3
    assert second_payload["skip"] == 2
    assert second_payload["limit"] == 2
    assert [book["title"] for book in second_payload["items"]] == ["Third"]


def test_get_books_rejects_invalid_pagination_params():
    assert client.get("/books/", params={"skip": -1}).status_code == 422
    assert client.get("/books/", params={"limit": 0}).status_code == 422


def test_delete_book():
    created = create_book("Delete me").json()

    delete_response = client.delete(f"/books/{created['id']}")
    get_response = client.get(f"/books/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
