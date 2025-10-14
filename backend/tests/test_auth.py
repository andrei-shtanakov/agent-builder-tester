"""Tests for authentication service and API."""

from backend.app import schemas
from backend.app.core.security import (
    create_user_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from backend.app.services import user_service


def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_user(db_session):
    """Test user creation."""
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
        full_name="Test User",
    )
    user = user_service.create_user(db_session, user_data)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.hashed_password != "password123"


def test_get_user_by_email(db_session):
    """Test getting user by email."""
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
    )
    created_user = user_service.create_user(db_session, user_data)

    user = user_service.get_user_by_email(db_session, "test@example.com")
    assert user is not None
    assert user.id == created_user.id
    assert user.email == "test@example.com"


def test_get_user_by_username(db_session):
    """Test getting user by username."""
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
    )
    created_user = user_service.create_user(db_session, user_data)

    user = user_service.get_user_by_username(db_session, "testuser")
    assert user is not None
    assert user.id == created_user.id
    assert user.username == "testuser"


def test_authenticate_user_success(db_session):
    """Test successful user authentication."""
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
    )
    user_service.create_user(db_session, user_data)

    # Test authentication with username
    user = user_service.authenticate_user(db_session, "testuser", "password123")
    assert user is not None
    assert user.username == "testuser"

    # Test authentication with email
    user = user_service.authenticate_user(db_session, "test@example.com", "password123")
    assert user is not None
    assert user.email == "test@example.com"


def test_authenticate_user_failure(db_session):
    """Test failed user authentication."""
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
    )
    user_service.create_user(db_session, user_data)

    # Wrong password
    user = user_service.authenticate_user(db_session, "testuser", "wrongpassword")
    assert user is None

    # Non-existent user
    user = user_service.authenticate_user(db_session, "nonexistent", "password123")
    assert user is None


def test_update_user(db_session):
    """Test user update."""
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
    )
    created_user = user_service.create_user(db_session, user_data)

    update_data = schemas.UserUpdate(
        full_name="Updated Name",
        email="newemail@example.com",
    )
    updated_user = user_service.update_user(db_session, created_user.id, update_data)

    assert updated_user is not None
    assert updated_user.full_name == "Updated Name"
    assert updated_user.email == "newemail@example.com"
    assert updated_user.username == "testuser"  # Should not change


def test_update_user_password(db_session):
    """Test password update."""
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="oldpassword",
    )
    created_user = user_service.create_user(db_session, user_data)
    old_hash = created_user.hashed_password

    update_data = schemas.UserUpdate(password="newpassword")
    updated_user = user_service.update_user(db_session, created_user.id, update_data)

    assert updated_user is not None
    assert updated_user.hashed_password != old_hash
    assert verify_password("newpassword", updated_user.hashed_password)


def test_list_users(db_session):
    """Test listing users."""
    for i in range(3):
        user_data = schemas.UserCreate(
            email=f"user{i}@example.com",
            username=f"user{i}",
            password="password123",
        )
        user_service.create_user(db_session, user_data)

    users = user_service.list_users(db_session)
    assert len(users) == 3


def test_delete_user(db_session):
    """Test user deletion."""
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
    )
    created_user = user_service.create_user(db_session, user_data)

    success = user_service.delete_user(db_session, created_user.id)
    assert success is True

    user = user_service.get_user_by_id(db_session, created_user.id)
    assert user is None


def test_jwt_token_creation_and_decoding():
    """Test JWT token creation and decoding."""
    from uuid import uuid4

    user_id = uuid4()
    username = "testuser"

    token = create_user_token(user_id, username)
    assert token is not None
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert payload["username"] == username


def test_jwt_token_invalid():
    """Test invalid JWT token."""
    invalid_token = "invalid.token.here"
    payload = decode_access_token(invalid_token)
    assert payload is None


def test_update_last_login(db_session):
    """Test updating last login timestamp."""
    user_data = schemas.UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123",
    )
    created_user = user_service.create_user(db_session, user_data)

    assert created_user.last_login is None

    user_service.update_last_login(db_session, created_user.id)

    updated_user = user_service.get_user_by_id(db_session, created_user.id)
    assert updated_user is not None
    assert updated_user.last_login is not None
