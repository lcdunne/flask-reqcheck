from functools import wraps
from typing import Callable, Type

from flask import g
from pydantic import BaseModel

from flask_request_check.request_validation import (
    BodyDataValidator,
    FormDataValidator,
    PathParameterValidator,
    QueryParameterValidator,
)
from flask_request_check.valid_request import get_valid_request


def validate(
    body: Type[BaseModel] | None = None,
    query: Type[BaseModel] | None = None,
    path: Type[BaseModel] | None = None,
    form: Type[BaseModel] | None = None,
) -> Callable:
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()
            validated.path_params = PathParameterValidator(path).validate(f)
            validated.query_params = QueryParameterValidator(query).validate()
            validated.body = BodyDataValidator(body).validate()
            validated.form = FormDataValidator(form).validate()

            g.valid_request = validated

            return f(*args, **kwargs)

        return wrapper

    return decorator
