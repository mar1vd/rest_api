from flasgger import Swagger
from flask import Flask
from flask_restful import Api

from api.books import BookResource, BooksResource
from repository.book_repository import BookRepository


def create_app(repository=None):
    app = Flask(__name__)
    api = Api(app)
    repository = repository or BookRepository()

    Swagger(
        app,
        template={
            "swagger": "2.0",
            "info": {
                "title": "Library API",
                "description": "Flask RESTful API for a library",
                "version": "1.0.0",
            },
            "basePath": "/",
        },
    )

    resource_kwargs = {"repository": repository}
    api.add_resource(
        BooksResource,
        "/books",
        "/books/",
        resource_class_kwargs=resource_kwargs,
    )
    api.add_resource(
        BookResource,
        "/books/<string:book_id>",
        resource_class_kwargs=resource_kwargs,
    )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
