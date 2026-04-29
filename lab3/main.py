from fastapi import FastAPI
from api.books import router
from core.database import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router)