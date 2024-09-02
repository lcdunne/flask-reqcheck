from inspect import getfullargspec
from typing import Any, Callable

from flask import request


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
