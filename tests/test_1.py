from flask_reqcheck.decoration import validate


def test_main(client):
    assert client
