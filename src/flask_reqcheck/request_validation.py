import json
from typing import Any, Type

from pydantic import BaseModel, TypeAdapter, ValidationError, create_model


class PathParameterValidator:
    """
    A class for validating path parameters.

    :param model: The Pydantic model to validate the path parameters against.
    :type model: Type[BaseModel] | None
    :param view_args: A mapping of URL path parameter names and their values. These URL
        path parameters are those from the URL for a given view function. If using
        Flask's built-in type converters, the values of this dictionary will already be
        valid; however, the type-hints given in the view function's signature take
        precedence.
    :type view_args: dict[str, str] | None
    :param function_arg_types: A mapping of function argument names to their types.
        Unlike the `view_args`, these are directly taken from the function signature and
        take precedence over view_args if given.
    :type function_arg_types: dict[str, Any] | None
    """

    def __init__(
        self,
        view_args: dict[str, str],
        model: Type[BaseModel] | None = None,
        function_arg_types: dict[str, Any] | None = None,
    ):
        self.model = model
        self.view_args = view_args or {}
        self.function_arg_types = function_arg_types or {}

    def validate(self) -> BaseModel | None:
        """
        Validate path parameters.

        This method retrieves the path parameters and attempts to validate them. If a
        model is provided, it validates the parameters against the model. If no model is
        provided, it validates the parameters against the type hints in the function
        declaration. If no type hints are given, flask's default validation will be
        used as a fallback.

        :return: The validated path parameters as a BaseModel instance, or None if no
            parameters are found.
        :rtype: BaseModel | None
        """
        if self.model is not None:
            return as_model(self.view_args, self.model)
        return self.validate_from_declaration()

    def validate_from_declaration(self) -> BaseModel:
        """
        Validate path parameters from the function declaration.

        Uses the type hints in the function signature to validate the request url
        parameters.

        :return: The Pydantic schema that defines the valid path parameters.
        :rtype: BaseModel
        """
        validated_path_params = self.validate_path_params()

        path_model = self.model or create_dynamic_model(
            "PathParams", **validated_path_params
        )

        return path_model.model_validate(validated_path_params)

    def validate_path_params(self) -> dict[str, Any]:
        """
        Validates path parameters against the expected types from the function
        declaration.

        This method iterates over the provided path parameters, determines the expected
        type for each parameter based on the function's type hints, and validates the
        value against that type. The validated parameters are then returned as a
        dictionary.

        :return: A dictionary containing the validated path parameters.
        :rtype: dict[str, Any]
        """
        validated_path_params = {}
        for arg, value in self.view_args.items():
            target_type = self.function_arg_types.get(arg, type(value))
            validated_value = TypeAdapter(target_type).validate_python(value)
            validated_path_params[arg] = validated_value
        return validated_path_params


class QueryParameterValidator:
    """
    Validates query parameters against a Pydantic model.

    This class is responsible for extracting query parameters from the Flask request,
    and validating them against a provided Pydantic model. If no model is provided,
    it logs a warning and returns without validation.
    """

    def __init__(
        self,
        model: Type[BaseModel],
        query_params: dict[str, Any],
    ):
        """
        Initializes the QueryParameterValidator with an optional Pydantic model.

        :param model: The Pydantic model to validate query parameters against.
        :type model: Type[BaseModel] | None
        :param query_params: The query parameters extracted from the request object.
        :type query_params: dict[str, Any] | None
        """
        self.model = model
        self.query_params = query_params

    def validate(self) -> BaseModel | None:
        """
        Validates query parameters against the provided model.

        Extracts query parameters from the Flask request, and attempts to validate them
        against the model provided during initialization. If no model is provided, logs
        a warning and returns without validation.

        :return: The validated query parameters as a Pydantic model instance.
        :rtype: BaseModel | None
        """
        return as_model(self.query_params, self.model)


class BodyDataValidator:
    """
    Validates the body data of a Flask request against a Pydantic model.

    This class is designed to validate the body data of a Flask request against a
    provided Pydantic model. It checks if the request has a body, if the body is in
    JSON format, and if the model is provided. If all conditions are met, it attempts
    to validate the request body against the model and returns the validated data.
    If any condition fails, it returns None or aborts the request with a 400 error.
    """

    def __init__(self, model: Type[BaseModel], body: dict[str, Any]):
        """
        Initializes the BodyDataValidator with an optional Pydantic model.

        :param model: The Pydantic model to validate the request body against.
        :type model: Type[BaseModel] | None
        """
        self.model = model
        self.body = body

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
        return as_model(self.body, self.model)


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

    def __init__(self, model: Type[BaseModel], form: dict[str, Any]):
        """
        Initializes the FormDataValidator with an optional Pydantic model.

        :param model: The Pydantic model to validate the request form data against.
        :type model: Type[BaseModel] | None
        """
        self.model = model
        self.form = form

    def validate(self) -> BaseModel | None:
        """
        Validates the request form data against the provided model.

        This method attempts to validate the request form data against the model
        and returns the validated data. If validation fails or no model is provided,
        it returns None or aborts the request with a 400 error.

        :return: The validated request form data as a Pydantic model instance, or None
            if validation fails or no model is provided.
        :rtype: BaseModel | None
        """
        return as_model(self.form, self.model)


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


def as_model(data: dict, model: Type[BaseModel]) -> BaseModel:
    """
    Attempts to validate the provided data against a Pydantic model.

    This function takes a dictionary of data and an optional Pydantic model. If a model
    is provided, it attempts to validate the data against the model. If validation is
    successful, it returns an instance of the model. If validation fails or no model is
    provided, it returns None or aborts the request with a 400 error.

    :param data: The data to be validated.
    :type data: dict
    :param model: The Pydantic model to validate the data against.
    :type model: Type[BaseModel]
    :return: The validated data as a Pydantic model instance
    :rtype: BaseModel | None
    """
    return model.model_validate(data)


def validation_error_to_json(e: ValidationError):
    return json.loads(e.json())
