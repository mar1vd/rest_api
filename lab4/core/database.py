import os

from pymongo import MongoClient


MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "library")

client = MongoClient(MONGO_URL)
database = client[MONGO_DB]
books_collection = database["books"]


def get_books_collection():
    return books_collection
