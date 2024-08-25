from functools import wraps
from typing import Callable, Type

from flask import g
from flask_reqcheck.request_validation import (
    BodyDataValidator,
    FormDataValidator,
    PathParameterValidator,
    QueryParameterValidator,
)
from flask_reqcheck.valid_request import get_valid_request
from pydantic import BaseModel


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


def validate_path(path: Type[BaseModel] | None = None) -> Callable:
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()
            validated.path_params = PathParameterValidator(path).validate(f)
            g.valid_request = validated
            return f(*args, **kwargs)

        return wrapper

    return decorator


def validate_query(query: Type[BaseModel] | None = None) -> Callable:
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()
            validated.query_params = QueryParameterValidator(query).validate()
            g.valid_request = validated
            return f(*args, **kwargs)

        return wrapper

    return decorator


def validate_body(body: Type[BaseModel] | None = None) -> Callable:
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()
            validated.body = BodyDataValidator(body).validate()
            g.valid_request = validated
            return f(*args, **kwargs)

        return wrapper

    return decorator


def validate_form(form: Type[BaseModel] | None = None) -> Callable:
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()
            validated.form = FormDataValidator(form).validate()
            g.valid_request = validated
            return f(*args, **kwargs)

        return wrapper

    return decorator
