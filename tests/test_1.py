from flask_request_check.decoration import validate


def test_main(client):
    assert client
