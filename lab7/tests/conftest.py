import os

os.environ["TESTING"] = "true"

import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from app.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker

if os.path.exists("test.db"):
    os.remove("test.db")

Base.metadata.create_all(bind=engine)

from app.main import app


@pytest.fixture(scope="function")
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def pytest_sessionfinish(session, exitstatus):
    if os.path.exists("test.db"):
        os.remove("test.db")