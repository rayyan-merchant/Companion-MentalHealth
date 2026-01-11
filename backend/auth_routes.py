"""
Authentication API routes for the Mental Health Companion application.
"""

from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends

from .auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    User,
    create_user,
    authenticate_user,
    create_access_token,
    get_current_user,
    user_to_response,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate):
    """
    Register a new user account.
    
    Returns a JWT token on successful registration.
    """
    # Validate email format (basic check)
    if "@" not in user_data.email or "." not in user_data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Validate password strength
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    # Create user
    user = create_user(user_data.email, user_data.password)
    
    # Generate token
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(
        access_token=access_token,
        user=user_to_response(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """
    Authenticate an existing user.
    
    Returns a JWT token on successful login.
    """
    user = authenticate_user(user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate token
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(
        access_token=access_token,
        user=user_to_response(user)
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint.
    
    Since JWT is stateless, logout is handled client-side by removing the token.
    This endpoint exists for API completeness and potential future features.
    """
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get the currently authenticated user's information.
    
    Requires a valid JWT token in the Authorization header.
    """
    return user_to_response(current_user)
