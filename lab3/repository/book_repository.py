from sqlalchemy.orm import Session
from models.book import Book


def get_books(db: Session, cursor, limit: int):
    query = db.query(Book).order_by(Book.id)
    if cursor:
        query = query.filter(Book.id > cursor)
    return query.limit(limit + 1).all()


def get_book_by_id(db: Session, book_id):
    return db.query(Book).filter(Book.id == book_id).first()


def create_book(db: Session, data):
    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id):
    book = get_book_by_id(db, book_id)
    if book:
        db.delete(book)
        db.commit()
        return True
    return False
