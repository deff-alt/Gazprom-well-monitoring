from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd_ctx.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    return pwd_ctx.verify(p, hashed)

def _make_token(sub: str, role: str, promysel_id: int | None, expires_delta: timedelta, token_type: str) -> str:
    payload = {
        "sub": sub,
        "role": role,
        "promysel_id": promysel_id,
        "type": token_type,
        "exp": datetime.now(timezone.utc) + expires_delta,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def create_access_token(sub: str, role: str, promysel_id: int | None) -> str:
    return _make_token(sub, role, promysel_id,
                       timedelta(minutes=settings.JWT_ACCESS_EXPIRES_MIN), "access")

def create_refresh_token(sub: str, role: str, promysel_id: int | None) -> str:
    return _make_token(sub, role, promysel_id,
                       timedelta(days=settings.JWT_REFRESH_EXPIRES_DAYS), "refresh")

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")