import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import Base, get_db
from backend.app.demo.seed_data import seed_database

# Use a file-based temporary sqlite db or isolated engine for tests
TEST_DB_URL = "sqlite:///./test_paypath.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def init_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSession()
    seed_database(db, force_reset=True)
    db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)
    import os
    if os.path.exists("./test_paypath.db"):
        try:
            os.remove("./test_paypath.db")
        except Exception:
            pass


@pytest.fixture(autouse=True)
def apply_db_override():
    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    # Keep consistent across tests
