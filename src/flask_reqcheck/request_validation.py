import json
from typing import Any, Type

from pydantic import BaseModel, TypeAdapter, ValidationError, create_model


def validate_path_parameters(
    view_args: dict[str, str],
    model: Type[BaseModel] | None = None,
    function_arg_types: dict[str, Any] | None = None,
) -> BaseModel:
    """Validates path parameters against a Pydantic model or dynamically based on
    function argument types.

    This function validates the path parameters provided in `view_args` against a
    Pydantic model specified by `model`. If `model` is not provided, it dynamically
    validates the path parameters based on the types specified in `function_arg_types`.
    If `function_arg_types` is not provided, it infers the types from the values in
    `view_args`.

    Parameters
    ----------
    view_args : dict[str, str]
        A dictionary containing the path parameter names as keys and their values as
        strings.
    model : Type[BaseModel] | None, optional
        The Pydantic model to validate the path parameters against. If not provided,
        dynamic validation is performed. Defaults to None.
    function_arg_types : dict[str, Any] | None, optional
        A dictionary specifying the expected types for each path parameter. If not
        provided, types are inferred from `view_args`. Defaults to None.

    Returns
    -------
    dict[str, Any]
        A dictionary containing the validated path parameters.
    """
    if model is not None:
        return model.model_validate(view_args)
    return _validate_path_parameters_from_function(view_args, function_arg_types or {})


def _validate_path_parameters_from_function(
    view_args: dict[str, str],
    function_arg_types: dict[str, Any] | None = None,
) -> BaseModel:
    """Validates path parameters based on the types specified in the function signature.

    This function validates the path parameters provided in `view_args` against the
    types specified in `function_arg_types`. It dynamically creates a Pydantic model
    based on the validated path parameters and then validates the path parameters
    against this model.

    Parameters
    ----------
    view_args : dict[str, str]
        A dictionary containing the path parameter names as keys and their values as
        strings.
    function_arg_types : dict[str, Any] | None, optional
        A dictionary specifying the expected types for each path parameter. If not
        provided, the type of the value in `view_args` is used.

    Returns
    -------
    BaseModel
        A Pydantic model instance containing the validated path parameters. The model is
        dynamically created from the `validated_path_params`.
    """
    validated_path_params = _infer_and_validate_path_param_types(
        view_args, function_arg_types
    )
    path_model = create_dynamic_model("PathParams", **validated_path_params)
    return path_model.model_validate(validated_path_params)


def _infer_and_validate_path_param_types(
    view_args: dict[str, Any], function_arg_types: dict[str, Any]
) -> dict[str, Any]:
    """Validates path parameters based on the types specified in the function signature.

    This function iterates over the provided `view_args` and for each argument, it
    determines the target type to validate against. If a type is explicitly specified
    in `function_arg_types`, it uses that; otherwise, it infers the type from the value
    itself. It then validates the value against the determined type and stores the
    validated value. Note that in the case that the type is not specified in
    `function_arg_types`, if the Flask endpoint url definition uses Flask's
    type adapters, then this will be used - otherwise, the default will be strings.

    Parameters
    ----------
    view_args : dict[str, Any]
        A dictionary containing the path parameter names as keys and their values as
        strings or other types.
    function_arg_types : dict[str, Any]
        A dictionary specifying the expected types for each path parameter.

    Returns
    -------
    dict[str, Any]
        A dictionary containing the validated path parameters.
    """
    validated_path_params = {}
    for arg, value in view_args.items():
        target_type = function_arg_types.get(arg, type(value))  # Infers here
        validated_path_params[arg] = TypeAdapter(target_type).validate_python(value)
    return validated_path_params


def _validate_x(model: Type[BaseModel], data: dict[str, Any]) -> BaseModel:
    """Validates the provided data against the given Pydantic model.

    Parameters
    ----------
    model : Type[BaseModel]
        The Pydantic model to validate the data against.
    data : dict[str, Any]
        The data to be validated.

    Returns
    -------
    BaseModel
        The validated data as a Pydantic model instance .
    """
    return model.model_validate(data)


def validate_query_parameters(
    model: Type[BaseModel], query_parameters: dict[str, Any]
) -> BaseModel:
    """Validates query parameters against a given Pydantic model.

    Parameters
    ----------
    model : Type[BaseModel]
        The Pydantic model to validate the query parameters against.
    query_parameters : dict[str, Any]
        The query parameters to be validated.

    Returns
    -------
    BaseModel
        The validated query parameters as a Pydantic model instance.
    """
    return _validate_x(model, query_parameters)


def validate_body_data(model: Type[BaseModel], body_data: dict[str, Any]) -> BaseModel:
    """Validates the provided body data against the given Pydantic model.

    Parameters
    ----------
    model : Type[BaseModel]
        The Pydantic model to validate the body data against.
    body_data : dict[str, Any]
        The body data to be validated.

    Returns
    -------
    BaseModel
        The validated body data as a Pydantic model instance.
    """
    return _validate_x(model, body_data)


def validate_form_data(model: Type[BaseModel], form_data: dict[str, Any]) -> BaseModel:
    """Validates the provided form data against the given Pydantic model.

    Parameters
    ----------
    model : Type[BaseModel]
        The Pydantic model to validate the form data against.
    form_data : dict[str, Any]
        The form data to be validated.

    Returns
    -------
    BaseModel
        The validated form data as a Pydantic model instance.
    """
    return _validate_x(model, form_data)


def create_dynamic_model(name: str, **kwargs) -> Type[BaseModel]:
    """
    Creates a dynamic Pydantic BaseModel given a name and keyword arguments.

    This function dynamically generates a Pydantic BaseModel based on the provided name
    and keyword arguments. The keyword arguments are used to define the fields of the
    model, where the key is the field name and the value is the field type.

    Parameters
    ----------
    name : str
        The name of the dynamic model to be created.
    **kwargs
        Keyword arguments defining the fields of the model.

    Returns
    -------
    Type[BaseModel]
        A dynamically created Pydantic BaseModel.
    """
    fields = {arg: (type(val), ...) for arg, val in kwargs.items()}
    return create_model(name, **fields)  # type: ignore
