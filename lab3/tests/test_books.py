import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.books import get_db
from core.database import Base
from main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_book(title: str):
    return client.post(
        "/books/",
        json={
            "title": title,
            "author": "Me",
            "description": "Test",
            "year": 2024,
            "status": "available",
        },
    )


def test_create_book():
    res = create_book("Test")

    assert res.status_code == 201
    assert res.json()["title"] == "Test"


def test_get_books_uses_cursor_pagination():
    for title in ["First", "Second", "Third"]:
        assert create_book(title).status_code == 201

    first_page = client.get("/books/", params={"limit": 2})

    assert first_page.status_code == 200
    first_payload = first_page.json()
    assert len(first_payload["items"]) == 2
    assert first_payload["limit"] == 2
    assert first_payload["next_cursor"] is not None

    second_page = client.get(
        "/books/",
        params={"limit": 2, "cursor": first_payload["next_cursor"]},
    )

    assert second_page.status_code == 200
    second_payload = second_page.json()
    assert len(second_payload["items"]) == 1
    assert second_payload["next_cursor"] is None

    first_page_ids = {book["id"] for book in first_payload["items"]}
    second_page_ids = {book["id"] for book in second_payload["items"]}
    assert first_page_ids.isdisjoint(second_page_ids)


def test_get_books_rejects_invalid_limit():
    res = client.get("/books/", params={"limit": 0})

    assert res.status_code == 422
