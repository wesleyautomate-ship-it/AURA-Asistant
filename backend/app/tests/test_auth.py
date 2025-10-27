import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.core.models import Base
from app.core.utils import hash_password

# Test database URL (use SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    # Create only the tables required for auth tests to avoid unsupported types in SQLite.
    required_tables = [
        Base.metadata.tables["users"],
        Base.metadata.tables.get("user_sessions"),
        Base.metadata.tables.get("audit_logs"),
    ]
    tables = [table for table in required_tables if table is not None]
    Base.metadata.create_all(bind=engine, tables=tables)

    # Create test data
    db = TestingSessionLocal()
    try:
        # Insert test user
        db.execute(
            text(
                """
            INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, email_verified)
            VALUES (:email, :password_hash, :first_name, :last_name, :role, :is_active, :email_verified)
        """
            ),
            {
                "email": "test@example.com",
                "password_hash": hash_password("testpass123"),
                "first_name": "Test",
                "last_name": "User",
                "role": "agent",
                "is_active": True,
                "email_verified": True,
            },
        )
        db.commit()
    finally:
        db.close()

    with TestClient(app) as c:
        yield c

    # Clean up
    Base.metadata.drop_all(bind=engine, tables=tables)


def test_health_endpoint(client):
    """Test the health endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert "version" in data
    assert "dependencies" in data


def test_login_success(client):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    assert "user" in data

    user = data["user"]
    assert user["email"] == "test@example.com"
    assert user["first_name"] == "Test"
    assert user["last_name"] == "User"
    assert user["role"] == "agent"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "testpass123"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


def test_refresh_token_success(client):
    """Test successful token refresh"""
    # First login to get tokens
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )

    assert login_response.status_code == 200
    login_data = login_response.json()
    refresh_token = login_data["refresh_token"]

    # Now refresh the token
    refresh_response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )

    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()

    assert "access_token" in refresh_data
    assert refresh_data["token_type"] == "bearer"
    assert "expires_in" in refresh_data


def test_refresh_token_invalid(client):
    """Test refresh with invalid token"""
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "invalid_token"}
    )

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INVALID_TOKEN"
