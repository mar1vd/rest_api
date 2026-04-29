import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.security import create_access_token, create_refresh_token, decode_token
from schemas.auth_schema import AccessToken, RefreshTokenRequest, TokenPair


router = APIRouter(prefix="/auth", tags=["auth"])

DEMO_USERNAME = os.getenv("AUTH_USERNAME", "admin")
DEMO_PASSWORD = os.getenv("AUTH_PASSWORD", "secret")


@router.post("/token", response_model=TokenPair)
def generate_tokens(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != DEMO_USERNAME or form_data.password != DEMO_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(form_data.username),
        "refresh_token": create_refresh_token(form_data.username),
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=AccessToken)
def refresh_access_token(data: RefreshTokenRequest):
    username = decode_token(data.refresh_token, expected_type="refresh")
    return {
        "access_token": create_access_token(username),
        "token_type": "bearer",
    }
