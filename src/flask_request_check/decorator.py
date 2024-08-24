from functools import wraps
from typing import Callable, Type

from flask import g
from pydantic import BaseModel

from flask_request_check.request_validation import (
    validate_body_data,
    validate_form_data,
    validate_path_params,
    validate_query_params,
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
            validated.path_params = validate_path_params(f, path_model=path)
            validated.query_params = validate_query_params(query_model=query)
            validated.body = validate_body_data(body_model=body)
            validated.form = validate_form_data(form_model=form)

            g.valid_request = validated

            return f(*args, **kwargs)

        return wrapper

    return decorator
