from fastapi.testclient import TestClient
from lab1.main import app

client = TestClient(app)


def test_add_book():

    response = client.post(
        "/books/",
        json={
            "title": "Test Book",
            "author": "Author",
            "description": "Desc",
            "year": 2024,
            "status": "available"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"


def test_get_books():

    response = client.get("/books/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_book():

    res = client.post(
        "/books/",
        json={
            "title": "Delete Book",
            "author": "Author",
            "description": "Desc",
            "year": 2024,
            "status": "available"
        }
    )

    book_id = res.json()["id"]

    response = client.delete(f"/books/{book_id}")

    assert response.status_code == 204