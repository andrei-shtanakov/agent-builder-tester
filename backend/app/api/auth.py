"""Authentication API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.core.dependencies import get_current_active_user, get_current_superuser
from backend.app.core.security import create_user_token
from backend.app.database import get_db
from backend.app.middleware.rate_limit import limiter
from backend.app.services import user_service

router = APIRouter()


@router.post(
    "/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/hour")
def register(
    request: Request,
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
) -> models.User:
    """
    Register a new user.

    Rate limited to 5 requests per hour to prevent abuse.
    """
    # Check if email already exists
    existing_user = user_service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    existing_user = user_service.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    return user_service.create_user(db, user_data)


@router.post("/login", response_model=schemas.Token)
@limiter.limit("10/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Login with username/email and password.

    Returns a JWT access token.
    """
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Update last login
    user_service.update_last_login(db, user.id)

    # Create access token
    access_token = create_user_token(user.id, user.username)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.User)
def get_current_user_info(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """Get current authenticated user's information."""
    return current_user


@router.put("/me", response_model=schemas.User)
@limiter.limit("10/minute")
def update_current_user_info(
    request: Request,
    user_data: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> models.User:
    """Update current user's information."""
    updated_user = user_service.update_user(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return updated_user


@router.get("/users", response_model=list[schemas.User])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> list[models.User]:
    """List all users (superuser only)."""
    return user_service.list_users(db, skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(
    user_id: UUID,
    current_user: models.User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> models.User:
    """Get user by ID (superuser only)."""
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/users/{user_id}", response_model=schemas.User)
@limiter.limit("10/minute")
def update_user(
    request: Request,
    user_id: UUID,
    user_data: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> models.User:
    """Update user (superuser only)."""
    updated_user = user_service.update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return updated_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
def delete_user(
    request: Request,
    user_id: UUID,
    current_user: models.User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> None:
    """Delete user (superuser only)."""
    success = user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
