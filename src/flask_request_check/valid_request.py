from flask import g
from pydantic import BaseModel


class ValidRequest:
    def __init__(
        self,
        path_params: BaseModel | None = None,
        query_params: BaseModel | None = None,
        body: BaseModel | None = None,
        form: BaseModel | None = None,
        headers: BaseModel | None = None,
        cookies: BaseModel | None = None,
    ):
        self.path_params = path_params
        self.query_params = query_params
        self.body = body
        self.form = form
        self.headers = headers
        self.cookies = cookies


def get_valid_request() -> ValidRequest:
    print(g, g.__dict__)
    if "valid_request" not in g:
        g.valid_request = ValidRequest()
    return g.valid_request
