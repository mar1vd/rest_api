import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from api.books import get_book_repository
from core.rate_limiter import RateLimiterMiddleware
from main import app


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.expires = {}

    def incr(self, key):
        self.values[key] = self.values.get(key, 0) + 1
        return self.values[key]

    def expire(self, key, seconds):
        self.expires[key] = seconds
        return True

    def ttl(self, key):
        return self.expires.get(key, 60)

    def reset(self):
        self.values.clear()
        self.expires.clear()


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
fake_redis = FakeRedis()
RateLimiterMiddleware.redis_client_override = fake_redis


def override_book_repository():
    return repository


app.dependency_overrides[get_book_repository] = override_book_repository
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    repository.books.clear()
    fake_redis.reset()


def get_tokens():
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "secret"},
    )
    assert response.status_code == 200
    return response.json()


def auth_headers():
    tokens = get_tokens()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def create_book(title: str, headers):
    return client.post(
        "/books/",
        headers=headers,
        json={
            "title": title,
            "author": "Me",
            "description": "Test",
            "year": 2026,
            "status": "available",
        },
    )


def test_books_require_access_token():
    res = client.get("/books/")

    assert res.status_code == 401


def test_generate_tokens_and_refresh_access_token():
    tokens = get_tokens()

    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"

    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert refresh_response.status_code == 200
    refreshed = refresh_response.json()
    assert refreshed["access_token"]
    assert refreshed["token_type"] == "bearer"


def test_refresh_rejects_access_token():
    tokens = get_tokens()

    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["access_token"]},
    )

    assert refresh_response.status_code == 401


def test_create_book():
    headers = auth_headers()

    res = create_book("Test", headers)

    assert res.status_code == 201
    payload = res.json()
    assert payload["id"]
    assert payload["title"] == "Test"


def test_get_books_uses_limit_offset_pagination():
    headers = auth_headers()
    for title in ["First", "Second", "Third"]:
        assert create_book(title, headers).status_code == 201

    first_page = client.get("/books/", params={"skip": 0, "limit": 2}, headers=headers)

    assert first_page.status_code == 200
    first_payload = first_page.json()
    assert first_payload["total"] == 3
    assert first_payload["skip"] == 0
    assert first_payload["limit"] == 2
    assert [book["title"] for book in first_payload["items"]] == ["First", "Second"]

    second_page = client.get("/books/", params={"skip": 2, "limit": 2}, headers=headers)

    assert second_page.status_code == 200
    second_payload = second_page.json()
    assert second_payload["total"] == 3
    assert second_payload["skip"] == 2
    assert second_payload["limit"] == 2
    assert [book["title"] for book in second_payload["items"]] == ["Third"]


def test_get_books_rejects_invalid_pagination_params():
    headers = auth_headers()

    assert client.get("/books/", params={"skip": -1}, headers=headers).status_code == 422
    assert client.get("/books/", params={"limit": 0}, headers=headers).status_code == 422


def test_delete_book():
    headers = auth_headers()
    created = create_book("Delete me", headers).json()

    delete_response = client.delete(f"/books/{created['id']}", headers=headers)
    get_response = client.get(f"/books/{created['id']}", headers=headers)

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_anonymous_user_under_rate_limit_gets_200():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_anonymous_user_over_rate_limit_gets_429():
    assert client.get("/health").status_code == 200
    assert client.get("/health").status_code == 200

    response = client.get("/health")

    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded"


def test_authorized_user_under_rate_limit_gets_200():
    headers = auth_headers()

    response = client.get("/books/", headers=headers)

    assert response.status_code == 200


def test_authorized_user_over_rate_limit_gets_429():
    headers = auth_headers()

    for _ in range(10):
        assert client.get("/books/", headers=headers).status_code == 200

    response = client.get("/books/", headers=headers)

    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded"
