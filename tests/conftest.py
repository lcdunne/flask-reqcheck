import pytest

from app import app


@pytest.fixture
def client():
    with app.test_client() as client_:
        yield client_
