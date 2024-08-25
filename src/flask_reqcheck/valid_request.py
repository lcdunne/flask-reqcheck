from typing import Any

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

    def to_dict(self) -> dict[str, Any]:
        """Convert the instance of ValidRequest to a dictionary."""
        return {
            k: v.model_dump() if v is not None else v for k, v in self.__dict__.items()
        }


def get_valid_request() -> ValidRequest:
    """Get the valid request from the global context.

    If the valid request is not in the global context, creates a new one and store it.

    Returns
    -------
    ValidRequest
        The valid request instance.
    """
    if "valid_request" not in g:
        g.valid_request = ValidRequest()
    return g.valid_request
