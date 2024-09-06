from functools import wraps
from typing import Callable, Type

from flask import abort, g, request
from pydantic import BaseModel

from flask_reqcheck.request_validation import (
    validate_body_data,
    validate_form_data,
    validate_path_parameters,
    validate_query_parameters,
)
from flask_reqcheck.valid_request import get_valid_request
from flask_reqcheck.validation_utils import (
    extract_form_data_as_dict,
    extract_query_params_as_dict,
    get_function_arg_types,
    request_is_form,
)


def validate(
    body_model: Type[BaseModel] | None = None,
    query_model: Type[BaseModel] | None = None,
    path_model: Type[BaseModel] | None = None,
    form_model: Type[BaseModel] | None = None,
) -> Callable:
    """
    A decorator to validate Flask request data against Pydantic models.

    This decorator validates the request data against the provided Pydantic models for
    body, query, path, and form data. Inside a Flask route function that is decoarted
    with this function, we can access the validated request instance using the
    :func:`~valid_request.get_valid_request` helper function.

    :param body_model: The Pydantic model to validate the request body against.
    :type body_model: Type[BaseModel] | None
    :param query_model: The Pydantic model to validate the request query parameters
        against.
    :type query_model: Type[BaseModel] | None
    :param path_model: The Pydantic model to validate the request path parameters
        against.
    :type path_model: Type[BaseModel] | None
    :param form_model: The Pydantic model to validate the request form data against.
    :type form_model: Type[BaseModel] | None
    :return: A decorator function that validates the request data.
    :rtype: Callable
    """

    def decorator(f: Callable):
        fun_args = get_function_arg_types(f)

        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()

            if request.view_args:
                validated.path_params = validate_path_parameters(
                    request.view_args, path_model, fun_args
                )

            if query_model is not None:
                params_as_dict = extract_query_params_as_dict()
                validated.query_params = validate_query_parameters(
                    query_model, params_as_dict
                )

            if body_model is not None:
                request_body = request.get_json()
                validated.body = validate_body_data(body_model, request_body)
            elif form_model is not None:
                if not request_is_form():
                    abort(415)  # TODO: test
                form_data = extract_form_data_as_dict()
                validated.form = validate_form_data(form_model, form_data)

            g.valid_request = validated

            return f(*args, **kwargs)

        return wrapper

    return decorator


def validate_path(path_model: Type[BaseModel] | None = None) -> Callable:
    """
    A decorator to validate Flask request path parameters against a Pydantic model.

    :param path_model: The Pydantic model to validate the request path parameters
        against.
    :type path_model: Type[BaseModel] | None
    :return: A decorator function that validates the request path parameters.
    :rtype: Callable
    """

    def decorator(f: Callable):
        fun_args = get_function_arg_types(f)

        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()

            if not request.view_args:
                raise RuntimeError(
                    "No path parameters found on decorated view function."
                )

            validated.path_params = validate_path_parameters(
                request.view_args, path_model, fun_args
            )

            g.valid_request = validated

            return f(*args, **kwargs)

        return wrapper

    return decorator


def validate_query(query_model: Type[BaseModel]) -> Callable:
    """
    A decorator to validate Flask request query parameters against a Pydantic model.

    :param query_model: The Pydantic model to validate the request query parameters
        against.
    :type query_model: Type[BaseModel] | None
    :return: A decorator function that validates the request query parameters.
    :rtype: Callable
    """

    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()

            query_params = extract_query_params_as_dict()
            validated.query_params = validate_query_parameters(
                query_model, query_params
            )

            g.valid_request = validated

            return f(*args, **kwargs)

        return wrapper

    return decorator


def validate_body(body_model: Type[BaseModel]) -> Callable:
    """
    A decorator to validate Flask request body against a Pydantic model.

    :param body_model: The Pydantic model to validate the request body against.
    :type body_model: Type[BaseModel] | None
    :return: A decorator function that validates the request body.
    :rtype: Callable
    """

    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()
            request_body = request.get_json()
            validated.body = validate_body_data(body_model, request_body)
            g.valid_request = validated
            return f(*args, **kwargs)

        return wrapper

    return decorator


def validate_form(form_model: Type[BaseModel]) -> Callable:
    """
    A decorator to validate Flask request form data against a Pydantic model.

    :param form_model: The Pydantic model to validate the request form data against.
    :type form_model: Type[BaseModel] | None
    :return: A decorator function that validates the request form data.
    :rtype: Callable
    """

    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = get_valid_request()

            if not request_is_form():
                abort(415)  # TODO: Provide some message

            form_data = extract_form_data_as_dict()
            validated.form = validate_form_data(form_model, form_data)
            g.valid_request = validated
            return f(*args, **kwargs)

        return wrapper

    return decorator
