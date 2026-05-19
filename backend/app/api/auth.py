"""StartupOS AI — Auth API (JWT Register/Login)

Security hardened:
- bcrypt password hashing (via passlib)
- Rate limiting on login/register endpoints
- Proper JWT validation
"""

import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

from app.database import get_db
from app.config import get_settings
from app.models.db_models import User
from app.models.request_schemas import RegisterRequest, LoginRequest
from app.models.response_schemas import TokenResponse, UserResponse
from app.rate_limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()
security = HTTPBearer(auto_error=False)

# bcrypt password hashing — industry standard, slow-by-design to resist brute force
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return pwd_context.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against bcrypt hash."""
    # Handle legacy SHA-256 hashes (migration path)
    if "$" in stored_hash and not stored_hash.startswith("$2b$"):
        # Legacy format: salt$hash — reject and force re-registration
        logger.warning("Legacy SHA-256 hash detected, rejecting for security")
        return False
    return pwd_context.verify(password, stored_hash)


def create_token(user_id: str) -> str:
    """Create a JWT token for a user."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Dependency: extract and validate user from JWT token."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User | None:
    """Dependency: returns user if authenticated, None if not.
    Used for endpoints that work for both authenticated and anonymous users.
    """
    if credentials is None:
        return None
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


@router.post("/register", response_model=TokenResponse)
@limiter.limit("5/minute")
def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if email already exists
    existing = db.query(User).filter(User.email == body.email.lower().strip()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user with bcrypt hash
    user = User(
        email=body.email.lower().strip(),
        password_hash=hash_password(body.password),
        name=body.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(str(user.id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(User).filter(User.email == body.email.lower().strip()).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(str(user.id))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user
