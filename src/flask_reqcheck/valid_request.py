from typing import Any

from flask import g
from pydantic import BaseModel


class ValidRequest:
    """
    Represents a validated request with its various components.

    This class encapsulates the different parts of a request that have been validated
    against Pydantic models. It provides a way to store and convert these validated
    components into a dictionary for further processing.

    When inside a Flask request context, use the :func:`get_valid_request` helper
    function to retrieve an instance of this class with the validated data.

    :param path_params: The validated path parameters of the request.
    :type path_params: BaseModel | None
    :param query_params: The validated query parameters of the request.
    :type query_params: BaseModel or None
    :param body: The validated body of the request.
    :type body: BaseModel or None
    :param form: The validated form data of the request.
    :type form: BaseModel or None
    :param headers: The validated headers of the request.
    :type headers: BaseModel or None
    :param cookies: The validated cookies of the request.
    :type cookies: BaseModel or None
    """

    def __init__(
        self,
        path_params: BaseModel | None = None,
        query_params: BaseModel | None = None,
        body: BaseModel | None = None,
        form: BaseModel | None = None,
        headers: BaseModel | None = None,
        cookies: BaseModel | None = None,
    ):
        """
        Initializes a ValidRequest instance with its components.

        :param path_params: The validated path parameters of the request.
        :type path_params: BaseModel | None
        :param query_params: The validated query parameters of the request.
        :type query_params: BaseModel | None
        :param body: The validated body of the request.
        :type body: BaseModel | None
        :param form: The validated form data of the request.
        :type form: BaseModel | None
        :param headers: The validated headers of the request.
        :type headers: BaseModel | None
        :param cookies: The validated cookies of the request.
        :type cookies: BaseModel | None
        """
        self.path_params = path_params
        self.query_params = query_params
        self.body = body
        self.form = form
        self.headers = headers
        self.cookies = cookies

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the instance of ValidRequest to a dictionary.

        :return: A dictionary representation of the ValidRequest instance.
        :rtype: dict[str, Any]
        """
        return {
            k: v.model_dump() if v is not None else v for k, v in self.__dict__.items()
        }


def get_valid_request() -> ValidRequest:
    """
    Retrieves the valid request from the global context.

    If the valid request is not present in the global context, a new instance is
    created and stored.

    :return: The instance of the valid request.
    :rtype: ValidRequest
    """
    if "valid_request" not in g:
        g.valid_request = ValidRequest()
    return g.valid_request
