from http import HTTPStatus
from typing import Callable

from flask import Flask
from pydantic import ValidationError


def default_validation_error_handler(error: ValidationError):
    return error.errors(), HTTPStatus.UNPROCESSABLE_ENTITY


class ReqCheck:
    """The main Flask-ReqCheck extension class.

    Initialise this object like any other Flask extension. Supports the factory pattern.
    Initialising this will add a convenience error handler to the `ValidationError`.
    This is not strictly necessary - if using custom error handlers in your application,
    you may choose to simply register your own for `pydantic.ValidationError`. In that
    case you can skip initialising this extension entirely. Alternatively, you can use
    the `register_validation_error_handler` convenience method of this class to override
    the default.
    """

    def __init__(self, app: Flask | None = None):
        self._default_validation_error_handler = default_validation_error_handler

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        if not hasattr(app, "extensions"):
            app.extensions = {}

        app.extensions["flask-reqcheck"] = self

        self._register_error_handlers(app)

    def _register_error_handlers(self, app: Flask) -> None:
        self.register_validation_error_handler(app, default_validation_error_handler)

    def register_validation_error_handler(self, app: Flask, f: Callable) -> None:
        """Add a custom handler for `ValidationError`.

        Parameters
        ----------
        app : Flask
            The Flask application instance.
        f : Callable
            The callback function to run when the error is encountered.
        """
        app.register_error_handler(ValidationError, f)
