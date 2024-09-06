from inspect import getfullargspec
from typing import Any, Callable, ItemsView, Iterator

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
    return _extract_multi_to_dict(request.args.lists())


def extract_form_data_as_dict() -> dict[str, Any]:
    return _extract_multi_to_dict(request.form.to_dict(flat=False).items())


def _extract_multi_to_dict(
    data: dict[str, Any] | Iterator[tuple[str, list[str]]] | ItemsView[str, list[str]]
):
    return {key: values[0] if len(values) == 1 else values for key, values in data}


def request_has_body() -> bool:
    """
    Checks the Content-Type header to ensure that the request has a body.

    According to RFC7230 - 3.3. Message Body, the presence of a body in a request is
    signaled by the presence of a Content-Length or Transfer-Encoding header field.

    :return: True if the request has a body, False otherwise.
    :rtype: bool
    """
    return "Transfer-Encoding" in request.headers or "Content-Length" in request.headers


def request_is_form() -> bool:
    """
    Checks the Content-Type header to ensure that it is form data..

    :return: True if the request contains for mdata, False otherwise.
    :rtype: bool
    """
    return request.headers.get("Content-Type") in [
        "application/x-www-form-urlencoded",
        "multipart/form-data",
    ]
