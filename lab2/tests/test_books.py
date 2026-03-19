from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_book():
    res = client.post("/books/", json={
        "title": "Test",
        "author": "Me",
        "description": "Test",
        "year": 2024,
        "status": "available"
    })
    assert res.status_code == 201


def test_get_books():
    res = client.get("/books/")
    assert res.status_code == 200