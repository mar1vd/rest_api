import pytest

from main import create_app
from repository.book_repository import BookRepository


@pytest.fixture()
def client():
    app = create_app(BookRepository())
    app.config.update(TESTING=True)
    return app.test_client()


def create_book(client, title):
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


def test_create_book(client):
    response = create_book(client, "Test")

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["id"]
    assert payload["title"] == "Test"


def test_get_books_uses_limit_offset_pagination(client):
    for title in ["First", "Second", "Third"]:
        assert create_book(client, title).status_code == 201

    first_page = client.get("/books/?skip=0&limit=2")
    second_page = client.get("/books/?skip=2&limit=2")

    first_payload = first_page.get_json()
    second_payload = second_page.get_json()

    assert first_page.status_code == 200
    assert first_payload["total"] == 3
    assert first_payload["skip"] == 0
    assert first_payload["limit"] == 2
    assert [book["title"] for book in first_payload["items"]] == ["First", "Second"]

    assert second_page.status_code == 200
    assert second_payload["total"] == 3
    assert second_payload["skip"] == 2
    assert second_payload["limit"] == 2
    assert [book["title"] for book in second_payload["items"]] == ["Third"]


def test_get_book_by_id(client):
    created = create_book(client, "Find me").get_json()

    response = client.get(f"/books/{created['id']}")

    assert response.status_code == 200
    assert response.get_json()["title"] == "Find me"


def test_delete_book(client):
    created = create_book(client, "Delete me").get_json()

    delete_response = client.delete(f"/books/{created['id']}")
    get_response = client.get(f"/books/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_swagger_is_available(client):
    response = client.get("/apidocs/")

    assert response.status_code == 200
