from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import secrets

from .database import get_db
from .models import AppSettings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer(auto_error=False)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_jwt_secret(db: Session) -> str:
    """Get or create the JWT secret from database."""
    setting = db.query(AppSettings).filter(AppSettings.key == "jwt_secret").first()
    if not setting:
        # Generate new secret
        secret = secrets.token_urlsafe(32)
        setting = AppSettings(key="jwt_secret", value=secret)
        db.add(setting)
        db.commit()
    return setting.value


def create_access_token(db: Session) -> str:
    """Create a JWT access token valid for 24 hours."""
    secret = get_jwt_secret(db)
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode = {"exp": expire, "type": "access"}
    return jwt.encode(to_encode, secret, algorithm=ALGORITHM)


def is_password_set(db: Session) -> bool:
    """Check if a password has been configured."""
    setting = db.query(AppSettings).filter(AppSettings.key == "password_hash").first()
    return setting is not None


def set_password(db: Session, password: str) -> None:
    """Set the application password (first-time setup)."""
    if is_password_set(db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password already configured"
        )
    hashed = get_password_hash(password)
    setting = AppSettings(key="password_hash", value=hashed)
    db.add(setting)
    db.commit()


def authenticate(db: Session, password: str) -> Optional[str]:
    """Authenticate with password and return JWT token if valid."""
    setting = db.query(AppSettings).filter(AppSettings.key == "password_hash").first()
    if not setting:
        return None
    if not verify_password(password, setting.value):
        return None
    return create_access_token(db)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> bool:
    """Dependency to verify JWT token on protected routes."""
    # If no password set, allow access (first-time setup)
    if not is_password_set(db):
        return True

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        secret = get_jwt_secret(db)
        payload = jwt.decode(credentials.credentials, secret, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        return True
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
