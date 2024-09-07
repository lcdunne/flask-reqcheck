from collections.abc import ItemsView
from inspect import getfullargspec
from typing import Any, Callable, Iterator

from flask import request


def get_function_arg_types(f: Callable) -> dict[str, Any]:
    """Retrieves all function arguments and their corresponding type hints.

    This method excludes arguments for which no type hints are provided. If no
    arguments have type hints, it returns an empty dictionary.

    Parameters
    ----------
    f : Callable
        The function from which to extract argument type hints.

    Returns
    -------
    dict[str, Any]
        A dictionary containing function argument names as keys and their type
        hints as values.
    """
    spec = getfullargspec(f)
    return spec.annotations


def extract_query_params_as_dict() -> dict[str, Any]:
    """Extract query parameters from the Flask request as a dictionary.

    This method iterates over the query parameters in the Flask request and
    converts them into a dictionary. If a parameter has multiple values, it is
    stored as a list in the dictionary.

    Returns
    -------
    dict
        A dictionary containing the query parameters.
    """
    return _extract_multi_to_dict(request.args.lists())


def extract_form_data_as_dict() -> dict[str, Any]:
    return _extract_multi_to_dict(request.form.to_dict(flat=False).items())


def _extract_multi_to_dict(
    data: dict[str, Any] | Iterator[tuple[str, list[str]]] | ItemsView[str, list[str]]
) -> dict[str, Any]:
    """Convert multi-value data into a dictionary.

    This function takes an input that can be a dictionary, an iterator, or an ItemsView
    (for example, `dict_items`) containing keys and lists of values. It converts this
    input into a dictionary where each key maps to a single value if there is only one
    value in the list, or to the list itself if there are multiple values.

    Parameters
    ----------
    data : dict[str, Any] or Iterator[tuple[str, list[str]]] or ItemsView[str, list[str]]
        The input data to be converted. It can be a dictionary, an iterator, or an
        ItemsView where each key maps to a list of values.

    Returns
    -------
    dict[str, Any]
        A dictionary where each key maps to a single value or a list of values.
    """
    return {key: values[0] if len(values) == 1 else values for key, values in data}


def request_has_body() -> bool:
    """Check if the request has a body by examining the Content-Type header.

    According to RFC7230 - 3.3. Message Body, the presence of a body in a request is
    signaled by the presence of a Content-Length or Transfer-Encoding header field.

    Returns
    -------
    bool
        True if the request has a body, False otherwise.
    """
    return "Transfer-Encoding" in request.headers or "Content-Length" in request.headers


def request_is_form() -> bool:
    """Check if the request's Content-Type header indicates form data.

    Returns
    -------
    bool
        True if the request contains form data, False otherwise.
    """
    return request.headers.get("Content-Type") in [
        "application/x-www-form-urlencoded",
        "multipart/form-data",
    ]
