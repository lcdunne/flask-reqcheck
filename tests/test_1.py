from flask_request_check.decorator import validate


def test_main(client):
    assert client
