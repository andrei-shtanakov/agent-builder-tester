"""User service with authentication business logic."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.core.security import get_password_hash, verify_password


def get_user_by_email(db: Session, email: str) -> models.User | None:
    """
    Get user by email address.

    Args:
        db: Database session
        email: User email

    Returns:
        User model or None if not found
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> models.User | None:
    """
    Get user by username.

    Args:
        db: Database session
        username: Username

    Returns:
        User model or None if not found
    """
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: UUID) -> models.User | None:
    """
    Get user by ID.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User model or None if not found
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user_data: schemas.UserCreate) -> models.User:
    """
    Create a new user with hashed password.

    Args:
        db: Database session
        user_data: User creation data

    Returns:
        Created user model
    """
    hashed_password = get_password_hash(user_data.password)
    user = models.User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> models.User | None:
    """
    Authenticate a user by username/email and password.

    Args:
        db: Database session
        username: Username or email
        password: Plain text password

    Returns:
        User model if authentication succeeds, None otherwise
    """
    # Try to find user by username or email
    user = get_user_by_username(db, username)
    if not user:
        user = get_user_by_email(db, username)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def update_user(
    db: Session, user_id: UUID, user_data: schemas.UserUpdate
) -> models.User | None:
    """
    Update user information.

    Args:
        db: Database session
        user_id: User ID
        user_data: Update data

    Returns:
        Updated user or None if not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    update_dict = user_data.model_dump(exclude_unset=True)

    # Handle password update separately
    if "password" in update_dict:
        password = update_dict.pop("password")
        if password:
            update_dict["hashed_password"] = get_password_hash(password)

    for key, value in update_dict.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def update_last_login(db: Session, user_id: UUID) -> None:
    """
    Update user's last login timestamp.

    Args:
        db: Database session
        user_id: User ID
    """
    user = get_user_by_id(db, user_id)
    if user:
        user.last_login = datetime.now(timezone.utc)
        db.commit()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    """
    List all users with pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of users
    """
    return db.query(models.User).offset(skip).limit(limit).all()


def delete_user(db: Session, user_id: UUID) -> bool:
    """
    Delete a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        True if deleted, False if not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False

    db.delete(user)
    db.commit()
    return True


def get_first_user(db: Session) -> models.User | None:
    """Retrieve the first available user.

    Args:
        db: Database session

    Returns:
        First user or None when the table is empty
    """

    return db.query(models.User).order_by(models.User.created_at).first()


def ensure_default_user(db: Session) -> models.User:
    """Return an existing user or create a default guest user.

    Args:
        db: Database session

    Returns:
        User record representing the default guest account
    """

    user = get_user_by_username(db, DEFAULT_GUEST_USERNAME)
    if user:
        return user

    guest = schemas.UserCreate(
        email=DEFAULT_GUEST_EMAIL,
        username=DEFAULT_GUEST_USERNAME,
        password=DEFAULT_GUEST_PASSWORD,
        full_name="Guest User",
    )
    created = create_user(db, guest)
    created.is_superuser = True
    created.is_active = True
    db.commit()
    db.refresh(created)
    return created
DEFAULT_GUEST_USERNAME = "guest"
DEFAULT_GUEST_EMAIL = "guest@example.com"
DEFAULT_GUEST_PASSWORD = "GuestPass!123"
