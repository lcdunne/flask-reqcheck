import json
from functools import wraps
from inspect import getfullargspec
from typing import Any, Callable, Type

from flask import abort, current_app, g, request
from pydantic import BaseModel, TypeAdapter, ValidationError, create_model

from flask_reqcheck.valid_request import get_valid_request


def validate_path_params(
    f: Callable, path_model: Type[BaseModel] | None
) -> BaseModel | None:
    """
    In the case when path params are required but none are found, the request would
    fail with a 404 anyway.
    """
    path_params = get_args_from_route_declaration()  # arg: value
    if path_params:
        if path_model is not None:
            return validate_path_params_from_model(path_model, path_params)
        return validate_path_params_from_declaration(f, path_params)
    return


def get_args_from_route_declaration() -> dict[str, Any] | None:
    """Get all path parameters.

    This will extract a dict containing path parameters names and their corresponding
    values provided in the request.
    """
    return request.view_args


def validate_path_params_from_model(
    model: Type[BaseModel] | None, path_params: dict[str, Any]
) -> BaseModel | None:
    return as_model(path_params, model)


def validate_path_params_from_declaration(
    f: Callable,
    path_params: dict[str, Any],
    path_model: Type[BaseModel] | None = None,
) -> BaseModel:
    function_arg_types = get_function_arg_types(f)  # arg: type
    # Validate based on the function signature and its types if present
    #   ... otherwise, fallback on the defaults (flask type-converted).
    validated_path_params = {}
    for arg, value in path_params.items():
        target_type = function_arg_types.get(arg, type(value))
        x = TypeAdapter(target_type).validate_python(value)
        validated_path_params[arg] = x

    if path_model is None:
        path_model = create_dynamic_model("PathParams", **validated_path_params)

    return path_model.model_validate(validated_path_params)


def get_function_arg_types(f: Callable) -> dict[str, Any]:
    """Get all function args and their type hints.

    Excludes arguments for which no types are given. If no arguments are hinted,
    returns an empty dict.
    """
    spec = getfullargspec(f)
    return spec.annotations


def create_dynamic_model(name: str, **kwargs: Any) -> Type[BaseModel]:
    """Create a dynamic pydantic BaseModel given a name and kwargs."""
    fields = {arg: (type(val), ...) for arg, val in kwargs.items()}
    return create_model(name, **fields)  # type: ignore


def validate_query_params(query_model: Type[BaseModel] | None) -> BaseModel | None:
    query_params = extract_query_params_as_dict()
    if query_params and query_model is not None:
        return as_model(query_params, query_model)

    current_app.logger.warning(
        "Query parameters were submitted, but no `query_model` was added for validation"
    )
    return


def extract_query_params_as_dict() -> dict:
    """Extract query parameters to dict, accounting for arrays."""
    return {
        key: values[0] if len(values) == 1 else values
        for key, values in request.args.lists()
    }


def validate_body(body_model: Type[BaseModel] | None) -> BaseModel | None:
    if not request_has_body() or request.form:
        return

    request_body = request.get_json()  # Raises 415 if not json

    if request_body and body_model is None:
        abort(400, "Unexpected data was provided")

    return as_model(request_body, body_model)


def as_model(data: dict, model: Type[BaseModel] | None) -> BaseModel | None:
    if model is not None:
        try:
            return model(**data)  # .model_dump()
        except ValidationError as e:
            # Requires ability to register a custom error handler?
            abort(400, json.loads(e.json()))
    return


def request_has_body() -> bool:
    # RFC7230 - 3.3. Message Body: Presence of body in request is signaled by
    #   a Content-Length or Transfer-Encoding header field.
    return "Transfer-Encoding" in request.headers or "Content-Length" in request.headers


def validate_form_data(form_model: Type[BaseModel] | None):
    return as_model(request.form, form_model)


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
            validated.path_params = validate_path_params(f, path_model=path)
            validated.query_params = validate_query_params(query_model=query)
            validated.body = validate_body(body_model=body)
            validated.form = validate_form_data(form_model=form)
            g.valid_request = validated
            return f(*args, **kwargs)

        return wrapper

    return decorator
