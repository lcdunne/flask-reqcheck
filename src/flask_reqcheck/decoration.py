import json
from functools import wraps
from inspect import getfullargspec
from typing import Any, Callable

from flask import Request, abort, current_app, g, request
from pydantic import BaseModel, TypeAdapter, ValidationError

from flask_reqcheck.valid_request import ValidRequest


def validate_function_arg(arg_name: str, arg_value: Any) -> Any:
    return TypeAdapter(arg_name).validate_python(arg_value)


def validate_query_params(query_params: dict, query_model: BaseModel) -> dict:
    # Query params sent but query is None: End user might have just sent query params -> DO NOTHING
    # Query params not sent, but query not None: End user just didn't send query params -> DO NOTHING
    return as_model(query_params, query_model)


def validate_body(body: dict, body_model: BaseModel) -> dict:
    if body and body_model is None:
        # End user sent a body but dev didn't expect one
        abort(400, "Bad request")
    return as_model(body, body_model)


def as_model(data: dict, model: BaseModel | None) -> dict:
    # TODO: Handle case when user provides an array.
    if model is not None:
        try:
            return model(**data).model_dump()
        except ValidationError as e:
            abort(400, json.loads(e.json()))
    return {}


def has_body(request: Request) -> bool:
    # RFC7230 - 3.3. Message Body: Presence of body in request is signaled by
    #   a Content-Length or Transfer-Encoding header field.
    return "Transfer-Encoding" in request.headers or "Content-Length" in request.headers


def validate_form_params(form_data: dict, form_model: BaseModel):
    return as_model(form_data, form_model)


def get_function_arg_types(f: Callable) -> dict[str, Any]:
    """Get all function args and their type hints.

    Excludes arguments for which no types are given. If no arguments are hinted,
    returns an empty dict.
    """
    spec = getfullargspec(f)
    return spec.annotations


def get_args_from_route_declaration() -> dict[str, Any]:
    """Get all path parameters."""
    return request.view_args


def validate_path_param(param: Any, expected: type):
    print(param, expected)


def validate_path_params_from_model(
    model: BaseModel, path_params: dict[str, Any]
) -> dict[str, Any]:
    return model.model_validate(path_params).model_dump()


def validate_path_params_from_declaration(
    f: Callable, path_params: dict[str, Any]
) -> dict[str, Any]:
    function_arg_types = get_function_arg_types(f)  # arg: type
    # Validate based on the function signature and its types if present
    #   ... otherwise, fallback on the defaults (flask type-converted).
    validated_path_params = {}
    for arg, value in path_params.items():
        # Iterate all given args and find the
        target_type = function_arg_types.get(arg)
        if not target_type:
            target_type = type(value)
            current_app.logger.debug(
                "No validation for %s=%s (defaulting to str)", arg, value
            )
        x = TypeAdapter(target_type).validate_python(value)
        validated_path_params[arg] = x
    return validated_path_params


def validate_path_params(
    f: Callable, path_model: BaseModel
) -> dict[str, Any] | BaseModel | None:
    path_params = get_args_from_route_declaration()  # arg: value
    if path_params:
        if path_model is not None:
            return validate_path_params_from_model(path_model, path_params)
        return validate_path_params_from_declaration(f, path_params)
    return None


def validate(
    body: BaseModel | None = None,
    query: BaseModel | None = None,
    path: BaseModel | None = None,
    form: BaseModel | None = None,
) -> Callable:
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            validated = ValidRequest()

            validated.path_params = validate_path_params(f, path_model=path)
            print("Validated path parameters: ", validated.path_params)

            # Validate the query parameters ---------------------------------------------
            validated.query_params = validate_query_params(
                request.args.to_dict(), query
            )
            # ----------------------------------------------------------------------------

            # Validate the request body - may need some more attention
            request.body = None
            if has_body(request) and not request.form:
                # TODO: Two hasty assumptions: (1) body is JSON, (2) it is not a form
                # TODO: Check for is json
                request.body = validate_body(request.get_json(), body)

            if request.form:
                print(dir(request))
                request.form_data = validate_form_params(request.form, form)

            g.valid_request = validated
            return f(*args, **kwargs)

        return wrapper

    return decorator
