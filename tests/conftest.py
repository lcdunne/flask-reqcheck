import pytest

from example.app import app


@pytest.fixture
def client():
    with app.test_client() as client_:
        yield client_
