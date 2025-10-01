import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.auth.models import Base

def test_db_creation():
    TEST_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    assert True