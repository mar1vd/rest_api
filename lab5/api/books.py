from flask import request
from flask_restful import Resource

from services.book_service import (
    create_book,
    delete_book,
    get_book,
    list_books,
    validate_book_payload,
)


class BooksResource(Resource):
    def __init__(self, repository):
        self.repository = repository

    def get(self):
        """
        Get books with Limit-Offset pagination
        ---
        tags:
          - books
        parameters:
          - in: query
            name: skip
            type: integer
            minimum: 0
            default: 0
          - in: query
            name: limit
            type: integer
            minimum: 1
            maximum: 100
            default: 10
        responses:
          200:
            description: Paginated list of books
        """
        skip = request.args.get("skip", default=0, type=int)
        limit = request.args.get("limit", default=10, type=int)

        if skip < 0 or limit < 1 or limit > 100:
            return {"message": "Invalid pagination params."}, 400

        return list_books(self.repository, skip, limit), 200

    def post(self):
        """
        Create a new book
        ---
        tags:
          - books
        consumes:
          - application/json
        parameters:
          - in: body
            name: book
            required: true
            schema:
              type: object
              required:
                - title
                - author
                - year
              properties:
                title:
                  type: string
                author:
                  type: string
                description:
                  type: string
                year:
                  type: integer
                status:
                  type: string
        responses:
          201:
            description: Book created
          400:
            description: Invalid request body
        """
        data = request.get_json(silent=True)
        error = validate_book_payload(data)
        if error:
            return {"message": error}, 400

        return create_book(self.repository, data), 201


class BookResource(Resource):
    def __init__(self, repository):
        self.repository = repository

    def get(self, book_id):
        """
        Get a book by id
        ---
        tags:
          - books
        parameters:
          - in: path
            name: book_id
            required: true
            type: string
        responses:
          200:
            description: Book found
          404:
            description: Book not found
        """
        book = get_book(self.repository, book_id)
        if not book:
            return {"message": "Book not found."}, 404
        return book, 200

    def delete(self, book_id):
        """
        Delete a book by id
        ---
        tags:
          - books
        parameters:
          - in: path
            name: book_id
            required: true
            type: string
        responses:
          204:
            description: Book deleted
          404:
            description: Book not found
        """
        deleted = delete_book(self.repository, book_id)
        if not deleted:
            return {"message": "Book not found."}, 404
        return "", 204
