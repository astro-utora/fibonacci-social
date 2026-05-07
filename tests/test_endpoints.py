import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv
from datetime import datetime
from uuid import uuid4

from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app.models import UserDB, TelegramUser, AuthUser, AuthProvider

# Load environment variables
load_dotenv()

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(db_session):
    """Create a test user with telegram auth"""
    user = UserDB(
        uuid=uuid4(),
        name="Test User",
        location="Test Location",
        role="Test Role",
        workplace="Test Workplace",
        birth_date="1990-01-01",
        goals="Test Goals",
        education="Test Education",
        phone_number="+1234567890"
    )
    db_session.add(user)
    db_session.flush()

    auth_user = AuthUser(
        user_uuid=user.uuid,
        provider=AuthProvider.TELEGRAM
    )
    db_session.add(auth_user)
    db_session.flush()

    telegram_user = TelegramUser(
        auth_id=auth_user.id,
        telegram_id=12345
    )
    db_session.add(telegram_user)
    db_session.commit()
    
    return user

def test_create_user():
    """Test user creation endpoint"""
    user_data = {
        "name": "New User",
        "location": "New Location",
        "role": "New Role",
        "workplace": "New Workplace",
        "birth_date": "1995-01-01",
        "goals": "New Goals",
        "education": "New Education",
        "phone_number": "+9876543210",
        "telegram_id": 67890
    }
    
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "uuid" in data
    assert data["status"] == "success"

def test_get_user(test_user):
    """Test get user endpoint"""
    response = client.get(f"/api/users/{test_user.uuid}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_user.name
    assert data["location"] == test_user.location

def test_verify_referral(test_user, db_session):
    """Test referral verification endpoint"""
    # First request should succeed
    response = client.get(f"/api/users/verify-referral/{test_user.referral_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_user.name
    assert data["uuid"] == str(test_user.uuid)

    # Invalid referral code should fail
    response = client.get("/api/users/verify-referral/invalid_code")
    assert response.status_code == 404

def test_telegram_login(test_user):
    """Test Telegram login endpoint"""
    auth_data = {
        "id": 12345,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "auth_date": int(datetime.now().timestamp()),
        "hash": "dummy_hash"  # We'll need to mock verify_telegram_data
    }
    
    # Mock verify_telegram_data to always return True for testing
    from unittest.mock import patch
    with patch('backend.app.routers.auth.verify_telegram_data', return_value=True):
        response = client.post("/api/auth/telegram", json=auth_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "token" in data
        assert "user" in data

def test_telegram_login_invalid():
    """Test Telegram login with invalid data"""
    auth_data = {
        "id": 99999,  # Non-existent user
        "first_name": "Invalid",
        "last_name": "User",
        "username": "invaliduser",
        "auth_date": int(datetime.now().timestamp()),
        "hash": "invalid_hash"
    }
    
    with patch('backend.app.routers.auth.verify_telegram_data', return_value=False):
        response = client.post("/api/auth/telegram", json=auth_data)
        assert response.status_code == 401

def test_create_user_with_referral(test_user):
    """Test user creation with referral"""
    user_data = {
        "name": "Referred User",
        "location": "Referred Location",
        "role": "Referred Role",
        "workplace": "Referred Workplace",
        "birth_date": "1995-01-01",
        "goals": "Referred Goals",
        "education": "Referred Education",
        "phone_number": "+9876543210",
        "telegram_id": 67890,
        "referral": test_user.referral_code
    }
    
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "uuid" in data
    assert data["status"] == "success" 