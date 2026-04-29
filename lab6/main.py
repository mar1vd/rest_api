from fastapi import FastAPI
from api.auth import router as auth_router
from api.books import router

app = FastAPI(title="Library API with Token Auth")

app.include_router(auth_router)
app.include_router(router)
