from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from collections import defaultdict
from datetime import datetime, timedelta
import threading

from ..database import get_db, engine, Base
from ..auth import is_password_set, set_password, authenticate
from .. import models  # Ensure models are imported for table creation

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Simple in-memory rate limiter: max 10 attempts per IP per 5 minutes
_rate_limit_lock = threading.Lock()
_rate_limit_store: dict[str, list[datetime]] = defaultdict(list)
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW = timedelta(minutes=5)


def _check_rate_limit(request: Request):
    """Raise 429 if the caller has exceeded the login attempt threshold."""
    ip = request.client.host if request.client else "unknown"
    now = datetime.utcnow()
    cutoff = now - RATE_LIMIT_WINDOW
    with _rate_limit_lock:
        attempts = _rate_limit_store[ip]
        # Prune old entries
        _rate_limit_store[ip] = [t for t in attempts if t > cutoff]
        if len(_rate_limit_store[ip]) >= RATE_LIMIT_MAX:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Please wait 5 minutes before trying again.",
            )
        _rate_limit_store[ip].append(now)


def ensure_tables_exist():
    """Ensure all database tables exist."""
    Base.metadata.create_all(bind=engine)


class PasswordSetup(BaseModel):
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    password: str = Field(..., min_length=8, max_length=128)


class AuthStatusResponse(BaseModel):
    password_configured: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds


@router.get("/status", response_model=AuthStatusResponse)
def get_auth_status(db: Session = Depends(get_db)):
    """Check if the app has been configured with a password."""
    try:
        return AuthStatusResponse(password_configured=is_password_set(db))
    except OperationalError:
        # Table doesn't exist yet, create it
        ensure_tables_exist()
        return AuthStatusResponse(password_configured=False)


@router.post("/setup", response_model=TokenResponse)
def setup_password(request: Request, data: PasswordSetup, db: Session = Depends(get_db)):
    """First-time setup: create the application password."""
    _check_rate_limit(request)
    try:
        password_set = is_password_set(db)
    except OperationalError:
        # Table doesn't exist, create it
        ensure_tables_exist()
        password_set = False

    if password_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password already configured. Use /login instead."
        )
    set_password(db, data.password)
    token = authenticate(db, data.password)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with the application password."""
    _check_rate_limit(request)
    try:
        password_set = is_password_set(db)
    except OperationalError:
        ensure_tables_exist()
        password_set = False

    if not password_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password not configured. Use /setup first."
        )
    token = authenticate(db, data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    return TokenResponse(access_token=token)
