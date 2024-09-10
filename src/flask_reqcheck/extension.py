from http import HTTPStatus
from typing import Callable

from flask import Flask
from pydantic import ValidationError


def default_validation_error_handler(error: ValidationError):
    return error.errors(), HTTPStatus.UNPROCESSABLE_ENTITY


class ReqCheck:
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
        app.register_error_handler(ValidationError, f)
