import pytest
from fastapi.testclient import TestClient

from app.main import app, store


@pytest.fixture
def client():
    store.clear()
    with TestClient(app) as c:
        yield c
