import uuid

from flask import Blueprint

from flask_reqcheck import (
    get_valid_request,
    validate,
    validate_body,
    validate_path,
    validate_query,
)

from .schemas import BodyModel, FormModel, PathModel, QueryModel, QueryModelWithRequred

endpoints = Blueprint("endpoints", __name__)


@endpoints.get("/")
@validate()
def index():
    return {}


@endpoints.get("/path/untyped/<a>/<b>/<c>/<d>")
@validate()
def valid_untyped_path(a, b, c, d):
    vreq = get_valid_request()
    return vreq.to_dict()


@endpoints.get("/path/partially_typed/<a>/<b>/<c>/<d>")
@validate()
def valid_partially_typed_path(a, b: int, c: float, d):
    vreq = get_valid_request()
    return vreq.to_dict()


@endpoints.get("/path/converters/<string:a>/<int:b>/<int:c>/<uuid:d>")
@validate()  # doesn't get function args
def valid_flask_converters_path(a, b, c, d):
    vreq = get_valid_request()
    return vreq.to_dict()


@endpoints.get("/path/typed/<a>/<b>/<c>/<d>")
@validate_path()  # gets function args
def valid_path(a: str, b: int, c: float, d: uuid.UUID):
    vreq = get_valid_request()
    return vreq.to_dict()


@endpoints.get("/query")
@validate_query(query=QueryModel)
def request_with_query_parameters():
    vreq = get_valid_request()
    return vreq.to_dict()


@endpoints.get("/query_required")
@validate_query(query=QueryModelWithRequred)
def request_with_required_query_parameter():
    vreq = get_valid_request()
    return vreq.to_dict()


@endpoints.get("/query/with/path/<a>/<b>/<c>/<d>")
@validate_path(path=PathModel)
@validate_query(query=QueryModel)
def request_with_query_and_path_parameters(a, b, c, d):
    vreq = get_valid_request()
    return vreq.to_dict()


@endpoints.post("/body")
@validate_body(BodyModel)
def request_with_body():
    vreq = get_valid_request()
    return vreq.to_dict()


@endpoints.post("/form")
@validate(form=FormModel)
def request_with_form_data():
    vreq = get_valid_request()
    return vreq.to_dict()
