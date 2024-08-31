import json
from inspect import getfullargspec
from typing import Any, Callable, Type

from flask import abort, current_app, request
from pydantic import BaseModel, TypeAdapter, ValidationError, create_model


class PathParameterValidator:
    """
    A class for validating path parameters.

    :param model: The Pydantic model to validate the path parameters against.
    :type model: Type[BaseModel] | None
    """

    def __init__(self, model: Type[BaseModel] | None = None):
        self.model = model

    def validate(self, f: Callable) -> BaseModel | None:
        """
        Validate path parameters.

        This method retrieves the path parameters and attempts to validate them. If a
        model is provided, it validates the parameters against the model. If no model is
        provided, it validates the parameters against the type hints in the function
        declaration. If no type hints are given, flask's default validation will be
        used as a fallback.

        :param f: The function to validate against if no model is provided.
        :type f: Callable

        :return: The validated path parameters as a BaseModel instance, or None if no
            parameters are found.
        :rtype: BaseModel | None
        """
        path_params = self.get_args_from_route_declaration()  # arg: value
        if path_params:
            if self.model is not None:
                return self.validate_from_model(path_params)
            return self.validate_from_declaration(f, path_params)
        return

    def get_args_from_route_declaration(self) -> dict[str, Any] | None:
        """
        Get all path parameters.

        :return: A dictionary containing path parameter names and their corresponding values provided in the request.
        :rtype: dict[str, Any] | None
        """
        return request.view_args

    def validate_from_model(self, path_params: dict[str, Any]) -> BaseModel | None:
        """
        Validate path parameters against a provided model.

        This method attempts to validate the path parameters against the model provided in the
        constructor. If the validation is successful, it returns a BaseModel instance
        representing the validated parameters. If the validation fails or if no model is
        provided, it returns None.

        :param path_params: The path parameters to validate.
        :type path_params: dict[str, Any]
        :return: The validated path parameters as a BaseModel instance, or None if validation fails.
        :rtype: BaseModel | None
        """
        return as_model(path_params, self.model)

    def validate_from_declaration(
        self,
        f: Callable,
        path_params: dict[str, Any],
    ) -> BaseModel:
        """
        Validate path parameters from the function declaration.

        Uses the type hints in the function signature to validate the request url
        parameters.

        :param f: The Flask route function that handles the request to be validated.
        :type f: Callable
        :param path_params: The path parameters provided in the request.
        :type path_params: dict[str, Any]

        :return: The Pydantic schema that defines the valid path parameters.
        :rtype: BaseModel
        """
        function_arg_types = self.get_function_arg_types(f)
        validated_path_params = self.validate_path_params(
            path_params, function_arg_types
        )
        path_model = self.model or create_dynamic_model(
            "PathParams", **validated_path_params
        )

        return path_model.model_validate(validated_path_params)

    def get_function_arg_types(self, f: Callable) -> dict[str, Any]:
        """
        Retrieves all function arguments and their corresponding type hints.

        This method excludes arguments for which no type hints are provided. If no arguments have type hints,
        it returns an empty dictionary.

        :param f: The function from which to extract argument type hints.
        :type f: Callable
        :return: A dictionary containing function argument names as keys and their type hints as values.
        :rtype: dict[str, Any]
        """
        spec = getfullargspec(f)
        return spec.annotations

    def validate_path_params(
        self,
        path_params: dict[str, Any],
        function_arg_types: dict[str, Type],
    ) -> dict[str, Any]:
        """
        Validates path parameters against the expected types from the function
        declaration.

        This method iterates over the provided path parameters, determines the expected
        type for each parameter based on the function's type hints, and validates the
        value against that type. The validated parameters are then returned as a
        dictionary.

        :param path_params: The path parameters to validate.
        :type path_params: dict[str, Any]
        :param function_arg_types: The expected types for each parameter based on the
            function's type hints.
        :type function_arg_types: dict[str, Type]
        :return: A dictionary containing the validated path parameters.
        :rtype: dict[str, Any]
        """
        validated_path_params = {}
        for arg, value in path_params.items():
            target_type = self.get_target_type(arg, value, function_arg_types)
            validated_value = self.validate_value(value, target_type)
            validated_path_params[arg] = validated_value
        return validated_path_params

    def get_target_type(
        self, arg: str, value: Any, function_arg_types: dict[str, Type]
    ) -> Type:
        """
        Retrieves the expected type for a given argument based on the function's
        type hints. If no type hint is specified for the argument, it defaults to the
        type of the provided value.

        :param arg: The name of the argument for which to retrieve the expected type.
        :type arg: str
        :param value: The value of the argument, used to determine its type if no type
            hint is available.
        :type value: Any
        :param function_arg_types: A dictionary containing the expected types for each
            argument based on the function's type hints.
        :type function_arg_types: dict[str, Type]
        :return: The expected type for the given argument, or the type of the value if
            no type hint is specified.
        :rtype: Type
        """
        return function_arg_types.get(arg, type(value))

    def validate_value(self, value: Any, target_type: Type) -> Any:
        """
        Validate the value against the target type using Pydantic's TypeAdapter.

        :param value: The value to be validated.
        :type value: Any
        :param target_type: The type to validate the value against.
        :type target_type: Type
        :return: The validated value.
        :rtype: Any
        """
        return TypeAdapter(target_type).validate_python(value)


class QueryParameterValidator:
    """
    Validates query parameters against a Pydantic model.

    This class is responsible for extracting query parameters from the Flask request,
    and validating them against a provided Pydantic model. If no model is provided,
    it logs a warning and returns without validation.
    """

    def __init__(self, model: Type[BaseModel] | None = None):
        """
        Initializes the QueryParameterValidator with an optional Pydantic model.

        :param model: The Pydantic model to validate query parameters against.
        :type model: Type[BaseModel] | None
        """
        self.model = model

    def validate(self) -> BaseModel | None:
        """
        Validates query parameters against the provided model.

        Extracts query parameters from the Flask request, and attempts to validate them
        against the model provided during initialization. If no model is provided, logs
        a warning and returns without validation.

        :return: The validated query parameters as a Pydantic model instance, or None if
            validation fails or no model is provided.
        :rtype: BaseModel | None
        """
        query_params = self.extract_query_params_as_dict()
        if not query_params:
            return

        if self.model is None:
            current_app.logger.warning(
                "Query parameters were submitted, but no `query_model` was "
                "added for validation"
            )
            return

        return as_model(query_params, self.model)

    def extract_query_params_as_dict(self) -> dict:
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


class BodyDataValidator:
    """
    Validates the body data of a Flask request against a Pydantic model.

    This class is designed to validate the body data of a Flask request against a
    provided Pydantic model. It checks if the request has a body, if the body is in
    JSON format, and if the model is provided. If all conditions are met, it attempts
    to validate the request body against the model and returns the validated data.
    If any condition fails, it returns None or aborts the request with a 400 error.
    """

    def __init__(self, model: Type[BaseModel] | None = None):
        """
        Initializes the BodyDataValidator with an optional Pydantic model.

        :param model: The Pydantic model to validate the request body against.
        :type model: Type[BaseModel] | None
        """
        self.model = model

    def validate(self) -> BaseModel | None:
        """
        Validates the request body against the provided model.

        This method checks if the request has a body, if the body is in JSON format,
        and if the model is provided. If all conditions are met, it attempts to validate
        the request body against the model and returns the validated data. If any
        condition fails, it returns None or aborts the request with a 400 error.

        :return: The validated request body as a Pydantic model instance, or None if
            validation fails or no model is provided.
        :rtype: BaseModel | None
        """
        if not request_has_body() or request.form:
            return

        request_body = request.get_json()  # Raises 415 if not json
        if request_body and self.model is None:
            abort(400, "Unexpected data was provided")

        return as_model(request_body, self.model)


class FormDataValidator:
    """
    Validates the form data of a Flask request against a Pydantic model.

    This class is designed to validate the form data of a Flask request against a
    provided Pydantic model. It checks if the request has form data and if the
    model is provided. If both conditions are met, it attempts to validate the
    request form data against the model and returns the validated data. If any
    condition fails, it returns None or aborts the request with a 400 error.

    :param model: The Pydantic model to validate the request form data against.
    :type model: Type[BaseModel] | None

    :return: The validated request form data as a Pydantic model instance, or None if
        validation fails or no model is provided.
    :rtype: BaseModel | None
    """

    def __init__(self, model: Type[BaseModel] | None = None):
        """
        Initializes the FormDataValidator with an optional Pydantic model.

        :param model: The Pydantic model to validate the request form data against.
        :type model: Type[BaseModel] | None
        """
        self.model = model

    def validate(self) -> BaseModel | None:
        """
        Validates the request form data against the provided model.

        This method attempts to validate the request form data against the model
        and returns the validated data. If validation fails or no model is provided,
        it returns None or aborts the request with a 400 error.

        :return: The validated request form data as a Pydantic model instance, or None if
            validation fails or no model is provided.
        :rtype: BaseModel | None
        """
        return as_model(request.form, self.model)


def create_dynamic_model(name: str, **kwargs) -> Type[BaseModel]:
    """
    Creates a dynamic Pydantic BaseModel given a name and keyword arguments.

    This function dynamically generates a Pydantic BaseModel based on the provided name
    and keyword arguments. The keyword arguments are used to define the fields of the
    model, where the key is the field name and the value is the field type.

    :param name: The name of the dynamic model to be created.
    :type name: str
    :param kwargs: Keyword arguments defining the fields of the model.
    :return: A dynamically created Pydantic BaseModel.
    :rtype: Type[BaseModel]
    """
    fields = {arg: (type(val), ...) for arg, val in kwargs.items()}
    return create_model(name, **fields)  # type: ignore


def as_model(data: dict, model: Type[BaseModel] | None) -> BaseModel | None:
    """
    Attempts to validate the provided data against a Pydantic model.

    This function takes a dictionary of data and an optional Pydantic model. If a model
    is provided, it attempts to validate the data against the model. If validation is
    successful, it returns an instance of the model. If validation fails or no model is
    provided, it returns None or aborts the request with a 400 error.

    :param data: The data to be validated.
    :type data: dict
    :param model: The Pydantic model to validate the data against.
    :type model: Type[BaseModel] | None
    :return: The validated data as a Pydantic model instance, or None if validation
        fails or no model is provided.
    :rtype: BaseModel | None
    """
    if model is not None:
        try:
            # TODO: Find some way to fail here if an unrecognised parameter is provided.
            return model(**data)
        except ValidationError as e:
            # Requires ability to register a custom error handler?
            abort(400, json.loads(e.json()))
    return None


def request_has_body() -> bool:
    """
    Checks if the request has a body.

    According to RFC7230 - 3.3. Message Body, the presence of a body in a request is
    signaled by the presence of a Content-Length or Transfer-Encoding header field.

    :return: True if the request has a body, False otherwise.
    :rtype: bool
    """
    return "Transfer-Encoding" in request.headers or "Content-Length" in request.headers
