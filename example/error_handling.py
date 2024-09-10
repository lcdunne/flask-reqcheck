from datetime import datetime, timezone
from http import HTTPStatus

from pydantic import ValidationError


def custom_validation_error_handler(error: ValidationError):
    return {
        "errors": error.errors(),
        "time": datetime.now(timezone.utc),
    }, HTTPStatus.UNPROCESSABLE_ENTITY
