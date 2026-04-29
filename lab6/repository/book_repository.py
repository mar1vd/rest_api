from bson import ObjectId
from pymongo.collection import Collection


class MongoBookRepository:
    def __init__(self, collection: Collection):
        self.collection = collection

    def get_books(self, skip: int, limit: int):
        cursor = self.collection.find().sort("_id", 1).skip(skip).limit(limit)
        return [self._serialize(book) for book in cursor]

    def count_books(self):
        return self.collection.count_documents({})

    def get_book_by_id(self, book_id: str):
        if not ObjectId.is_valid(book_id):
            return None
        book = self.collection.find_one({"_id": ObjectId(book_id)})
        return self._serialize(book) if book else None

    def create_book(self, data):
        result = self.collection.insert_one(data.model_dump())
        book = self.collection.find_one({"_id": result.inserted_id})
        return self._serialize(book)

    def delete_book(self, book_id: str):
        if not ObjectId.is_valid(book_id):
            return False
        result = self.collection.delete_one({"_id": ObjectId(book_id)})
        return result.deleted_count == 1

    @staticmethod
    def _serialize(book):
        return {
            "id": str(book["_id"]),
            "title": book["title"],
            "author": book["author"],
            "description": book.get("description"),
            "year": book["year"],
            "status": book.get("status", "available"),
        }
