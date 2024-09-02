from functools import wraps
from inspect import getfullargspec
from typing import Any, Callable, Type

from flask import g, request
from pydantic import BaseModel

from flask_reqcheck.request_validation import (
    BodyDataValidator,
    FormDataValidator,
    PathParameterValidator,
    QueryParameterValidator,
)
from flask_reqcheck.valid_request import get_valid_request


def get_function_arg_types(f: Callable) -> dict[str, Any]:
    """
    Retrieves all function arguments and their corresponding type hints.

    This method excludes arguments for which no type hints are provided. If no
    arguments have type hints, it returns an empty dictionary.

    :param f: The function from which to extract argument type hints.
    :type f: Callable
    :return: A dictionary containing function argument names as keys and their type
        hints as values.
    :rtype: dict[str, Any]
    """
    spec = getfullargspec(f)
    return spec.annotations


def extract_query_params_as_dict() -> dict[str, Any]:
    """
    Extracts query parameters from the Flask request as a dictionary.

    This method iterates over the query parameters in the Flask request, and
    converts them into a dictionary. If a parameter has multiple values, it is
    stored as a list in the dictionary.

    :return: A dictionary containing the query parameters.
    :rtype: dict
    """
    return {
        key: values[0] if len(values) == 1 else values
        for key, values in request.args.lists()
    }


def request_has_body() -> bool:
    """
    Checks if the request has a body.

    According to RFC7230 - 3.3. Message Body, the presence of a body in a request is
    signaled by the presence of a Content-Length or Transfer-Encoding header field.

    :return: True if the request has a body, False otherwise.
    :rtype: bool
    """
    return "Transfer-Encoding" in request.headers or "Content-Length" in request.headers


def validate(
    body: Type[BaseModel] | None = None,
    query: Type[BaseModel] | None = None,
    path: Type[BaseModel] | None = None,
    form: Type[BaseModel] | None = None,
) -> Callable:
    """
    A decorator to validate Flask request data against Pydantic models.

    This decorator validates the request data against the provided Pydantic models for
    body, query, path, and form data. Inside a Flask route function that is decoarted
    with this function, we can access the validated request instance using the
    :func:`~valid_request.get_valid_request` helper function.

    :param body: The Pydantic model to validate the request body against.
    :type body: Type[BaseModel] | None
    :param query: The Pydantic model to validate the request query parameters against.
    :type query: Type[BaseModel] | None
    :param path: The Pydantic model to validate the request path parameters against.
    :type path: Type[BaseModel] | None
    :param form: The Pydantic model to validate the request form data against.
    :type form: Type[BaseModel] | None
    :return: A decorator function that validates the request data.
    :rtype: Callable
    """

    def decorator(f: Callable):
        fun_args = get_function_arg_types(f)

        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()

            validated.path_params = PathParameterValidator(
                path, request.view_args, fun_args
            ).validate()

            validated.query_params = QueryParameterValidator(
                query, extract_query_params_as_dict()
            ).validate()

            # Body/form is determined by the Content-Type header.
            if body:
                validated.body = BodyDataValidator(body, request.get_json()).validate()
            elif form:
                # TODO: Check here if header Content-Type is
                #  `application/x-www-form-urlencoded`?
                validated.form = FormDataValidator(form, request.form).validate()

            g.valid_request = validated

            return f(*args, **kwargs)

        return wrapper

    return decorator


def validate_path(path: Type[BaseModel] | None = None) -> Callable:
    """
    A decorator to validate Flask request path parameters against a Pydantic model.

    :param path: The Pydantic model to validate the request path parameters against.
    :type path: Type[BaseModel] | None
    :return: A decorator function that validates the request path parameters.
    :rtype: Callable
    """

    def decorator(f: Callable):
        fun_args = get_function_arg_types(f)

        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()

            validated.path_params = PathParameterValidator(
                path, request.view_args, fun_args
            ).validate()

            g.valid_request = validated
            return f(*args, **kwargs)

        return wrapper

    return decorator


def validate_query(query: Type[BaseModel]) -> Callable:
    """
    A decorator to validate Flask request query parameters against a Pydantic model.

    :param query: The Pydantic model to validate the request query parameters against.
    :type query: Type[BaseModel] | None
    :return: A decorator function that validates the request query parameters.
    :rtype: Callable
    """

    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()

            validated.query_params = QueryParameterValidator(
                query, extract_query_params_as_dict()
            ).validate()

            g.valid_request = validated

            return f(*args, **kwargs)

        return wrapper

    return decorator


def validate_body(body: Type[BaseModel]) -> Callable:
    """
    A decorator to validate Flask request body against a Pydantic model.

    :param body: The Pydantic model to validate the request body against.
    :type body: Type[BaseModel] | None
    :return: A decorator function that validates the request body.
    :rtype: Callable
    """

    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()
            validated.body = BodyDataValidator(body).validate()
            g.valid_request = validated
            return f(*args, **kwargs)

        return wrapper

    return decorator


def validate_form(form: Type[BaseModel]) -> Callable:
    """
    A decorator to validate Flask request form data against a Pydantic model.

    :param form: The Pydantic model to validate the request form data against.
    :type form: Type[BaseModel] | None
    :return: A decorator function that validates the request form data.
    :rtype: Callable
    """

    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()
            validated.form = FormDataValidator(form).validate()
            g.valid_request = validated
            return f(*args, **kwargs)

        return wrapper

    return decorator
