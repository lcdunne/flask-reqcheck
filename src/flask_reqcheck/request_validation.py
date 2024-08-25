import json
from inspect import getfullargspec
from typing import Any, Callable, Type

from flask import abort, current_app, request
from pydantic import BaseModel, TypeAdapter, ValidationError, create_model


class PathParameterValidator:
    def __init__(self, model: Type[BaseModel] | None = None):
        self.model = model

    def validate(self, f: Callable) -> BaseModel | None:
        """Validate path parameters

        This method retrieves the path parameters and attempts to validate them. If a
        model is provided, it validates the parameters against the model. If no model is
        provided, it validates the parameters against the type hints in the function
        declaration. If no type hints are given, flask's default validation will be
        used as a fallback.

        Parameters
        ----------
        f : Callable
            The function to validate against if no model is provided.

        Returns
        -------
        BaseModel | None
            The validated path parameters as a BaseModel instance, or None if no
            parameters are found.
        """
        path_params = self.get_args_from_route_declaration()  # arg: value
        if path_params:
            if self.model is not None:
                return self.validate_from_model(path_params)
            return self.validate_from_declaration(f, path_params)
        return

    def get_args_from_route_declaration(self) -> dict[str, Any] | None:
        """Get all path parameters.

        This will extract a dict containing path parameters names and their
        corresponding values provided in the request.
        """
        return request.view_args

    def validate_from_model(self, path_params: dict[str, Any]) -> BaseModel | None:
        return as_model(path_params, self.model)

    def validate_from_declaration(
        self, f: Callable, path_params: dict[str, Any]
    ) -> BaseModel:
        function_arg_types = self.get_function_arg_types(f)
        validated_path_params = self.validate_path_params(
            path_params, function_arg_types
        )
        path_model = self.model or create_dynamic_model(
            "PathParams", **validated_path_params
        )

        return path_model.model_validate(validated_path_params)

    def get_function_arg_types(self, f: Callable) -> dict[str, Any]:
        """Get all function args and their type hints.

        Excludes arguments for which no types are given. If no arguments are hinted,
        returns an empty dict.
        """
        spec = getfullargspec(f)
        return spec.annotations

    def validate_path_params(
        self,
        path_params: dict[str, Any],
        function_arg_types: dict[str, Type],
    ) -> dict[str, Any]:
        validated_path_params = {}
        for arg, value in path_params.items():
            target_type = self.get_target_type(arg, value, function_arg_types)
            validated_value = self.validate_value(value, target_type)
            validated_path_params[arg] = validated_value
        return validated_path_params

    def get_target_type(
        self, arg: str, value: Any, function_arg_types: dict[str, Type]
    ) -> Type:
        """Get the expected type for the given argument, falling back to the value's
        current type if not specified."""
        return function_arg_types.get(arg, type(value))

    def validate_value(self, value: Any, target_type: Type) -> Any:
        return TypeAdapter(target_type).validate_python(value)


class QueryParameterValidator:
    def __init__(self, model: Type[BaseModel] | None = None):
        self.model = model

    def validate(self) -> BaseModel | None:
        query_params = self.extract_query_params_as_dict()
        if query_params and self.model is not None:
            return as_model(query_params, self.model)

        current_app.logger.warning(
            "Query parameters were submitted, but no `query_model` was "
            "added for validation"
        )
        return

    def extract_query_params_as_dict(self) -> dict:
        """Extract query parameters to dict, accounting for arrays."""
        return {
            key: values[0] if len(values) == 1 else values
            for key, values in request.args.lists()
        }


class BodyDataValidator:
    def __init__(self, model: Type[BaseModel] | None = None):
        self.model = model

    def validate(self) -> BaseModel | None:
        if not request_has_body() or request.form:
            return

        request_body = request.get_json()  # Raises 415 if not json
        if request_body and self.model is None:
            abort(400, "Unexpected data was provided")

        return as_model(request_body, self.model)


class FormDataValidator:
    def __init__(self, model: Type[BaseModel] | None = None):
        self.model = model

    def validate(self):
        return as_model(request.form, self.model)


def create_dynamic_model(name: str, **kwargs) -> Type[BaseModel]:
    """Helper to create a dynamic pydantic BaseModel given a name and kwargs."""
    fields = {arg: (type(val), ...) for arg, val in kwargs.items()}
    return create_model(name, **fields)  # type: ignore


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
