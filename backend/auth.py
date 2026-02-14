"""
Authentication module for the Mental Health Companion application.
Handles user registration, login, JWT token management, and password hashing.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import json
import uuid
import os

from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# ============================================================================
# Configuration
# ============================================================================

# JWT Settings - In production, use environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "companion-mental-health-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
USERS_DIR = DATA_DIR / "users"
USERS_FILE = USERS_DIR / "users.json"


# ============================================================================
# Models
# ============================================================================

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: str
    password: str


class UserLogin(BaseModel):
    """Schema for user login"""
    email: str
    password: str


class UserResponse(BaseModel):
    """Schema for user data returned to client (no password)"""
    user_id: str
    email: str
    created_at: str


class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class User(BaseModel):
    """Internal user model with password hash"""
    user_id: str
    email: str
    password_hash: str
    created_at: str


# ============================================================================
# User Storage Functions
# ============================================================================

def _ensure_data_dirs():
    """Create data directories if they don't exist"""
    USERS_DIR.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        USERS_FILE.write_text("[]")


def _load_users() -> list[dict]:
    """Load all users from JSON file"""
    _ensure_data_dirs()
    try:
        return json.loads(USERS_FILE.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_users(users: list[dict]):
    """Save users to JSON file"""
    _ensure_data_dirs()
    USERS_FILE.write_text(json.dumps(users, indent=2))


def get_user_by_email(email: str) -> Optional[User]:
    """Find a user by email address"""
    users = _load_users()
    for user_data in users:
        if user_data["email"].lower() == email.lower():
            return User(**user_data)
    return None


def get_user_by_id(user_id: str) -> Optional[User]:
    """Find a user by ID"""
    users = _load_users()
    for user_data in users:
        if user_data["user_id"] == user_id:
            return User(**user_data)
    return None


def create_user(email: str, password: str) -> User:
    """Create a new user with hashed password"""
    users = _load_users()
    
    # Check if email already exists
    if get_user_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        user_id=str(uuid.uuid4()),
        email=email.lower(),
        password_hash=pwd_context.hash(password),
        created_at=datetime.utcnow().isoformat() + "Z"
    )
    
    users.append(user.model_dump())
    _save_users(users)
    
    return user


# ============================================================================
# Password Functions
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password"""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# ============================================================================
# JWT Functions
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ============================================================================
# Auth Dependencies
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    Use this in protected routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user


def user_to_response(user: User) -> UserResponse:
    """Convert internal User model to response model (without password)"""
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        created_at=user.created_at
    )
