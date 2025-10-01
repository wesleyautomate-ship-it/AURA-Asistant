import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from backend.auth.database import Base

if __name__ == "__main__":
    try:
        engine = test_engine()
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(e)