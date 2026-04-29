def list_books(repository, skip=0, limit=10):
    return {
        "items": repository.get_books(skip, limit),
        "total": repository.count_books(),
        "skip": skip,
        "limit": limit,
    }


def get_book(repository, book_id):
    return repository.get_book_by_id(book_id)


def create_new_book(repository, data):
    return repository.create_book(data)


def remove_book(repository, book_id):
    return repository.delete_book(book_id)
