REQUIRED_FIELDS = {"title", "author", "year"}


def validate_book_payload(data):
    if not isinstance(data, dict):
        return "Request body must be a JSON object."

    missing_fields = REQUIRED_FIELDS - data.keys()
    if missing_fields:
        fields = ", ".join(sorted(missing_fields))
        return f"Missing required fields: {fields}."

    if not isinstance(data["year"], int):
        return "Field 'year' must be an integer."

    return None


def list_books(repository, skip=0, limit=10):
    return {
        "items": repository.list_books(skip, limit),
        "total": repository.count_books(),
        "skip": skip,
        "limit": limit,
    }


def get_book(repository, book_id):
    return repository.get_book(book_id)


def create_book(repository, data):
    return repository.create_book(data)


def delete_book(repository, book_id):
    return repository.delete_book(book_id)
