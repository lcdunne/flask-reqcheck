from pydantic import BaseModel


class ValidRequest:
    """TODO: Re-init this at start of each request context"""

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
