import os

import redis
from fastapi import Request
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.security import ALGORITHM, SECRET_KEY, jwt


AUTHENTICATED_LIMIT = int(os.getenv("AUTHENTICATED_RATE_LIMIT", "10"))
ANONYMOUS_LIMIT = int(os.getenv("ANONYMOUS_RATE_LIMIT", "2"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
EXCLUDED_PATHS = {"/docs", "/openapi.json", "/redoc"}


def create_redis_client():
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    redis_client_override = None

    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis_client = (
            redis_client
            or self.redis_client_override
            or create_redis_client()
        )

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        key, limit = self._get_rate_limit_identity(request)
        current_count = self.redis_client.incr(key)

        if current_count == 1:
            self.redis_client.expire(key, RATE_LIMIT_WINDOW_SECONDS)

        if current_count > limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "limit": limit,
                    "retry_after": self._get_retry_after(key),
                },
            )

        return await call_next(request)

    def _get_rate_limit_identity(self, request: Request):
        authorization = request.headers.get("Authorization", "")
        if authorization.startswith("Bearer "):
            token = authorization.removeprefix("Bearer ").strip()
            username = self._decode_access_token_subject(token)
            if username:
                return f"rate-limit:auth:{username}", AUTHENTICATED_LIMIT

        client_host = request.client.host if request.client else "unknown"
        return f"rate-limit:anon:{client_host}", ANONYMOUS_LIMIT

    @staticmethod
    def _decode_access_token_subject(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "access":
                return None
            return payload.get("sub")
        except JWTError:
            return None

    def _get_retry_after(self, key: str):
        ttl = self.redis_client.ttl(key)
        return ttl if ttl > 0 else RATE_LIMIT_WINDOW_SECONDS
