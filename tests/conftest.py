import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.models import Base

TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def db_session(test_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()