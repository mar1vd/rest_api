from fastapi import FastAPI
from api.auth import router as auth_router
from api.books import router
from api.health import router as health_router
from core.rate_limiter import RateLimiterMiddleware

app = FastAPI(title="Library API with Token Auth and Rate Limiting")

app.add_middleware(RateLimiterMiddleware)
app.include_router(auth_router)
app.include_router(router)
app.include_router(health_router)
