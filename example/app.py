import uuid

from flask import Flask
from pydantic import BaseModel

from flask_request_check import validate
from flask_request_check.valid_request import get_valid_request

app = Flask(__name__)
setattr(app.json, "sort_keys", False)


class QueryModel(BaseModel):
    a: str | None = None
    b: int | None = None
    c: float | None = None
    d: uuid.UUID | None = None
    arr: list[int] | None = None
    x: str


class BodyModel(BaseModel):
    a: str
    b: int
    c: float
    d: uuid.UUID
    arr: list[int]


class FormModel(BaseModel):
    a: str
    b: int


@app.get("/")
@validate()
def index():
    return {}


@app.get("/path/untyped/<a>/<b>/<c>/<d>")
@validate()
def valid_untyped_path(a, b, c, d):
    vreq = get_valid_request()
    return {k: v.model_dump() if v is not None else v for k, v in vreq.__dict__.items()}


@app.get("/path/partially_typed/<a>/<b>/<c>/<d>")
@validate()
def valid_partially_typed_path(a, b: int, c: float, d):
    vreq = get_valid_request()
    return {k: v.model_dump() if v is not None else v for k, v in vreq.__dict__.items()}


@app.get("/path/typed/<a>/<b>/<c>/<d>")
@validate()
def valid_path(a: str, b: int, c: float, d: uuid.UUID):
    vreq = get_valid_request()
    return {k: v.model_dump() if v is not None else v for k, v in vreq.__dict__.items()}


@app.get("/query")
@validate(query=QueryModel)
def request_with_query_parameters():
    vreq = get_valid_request()
    return {k: v.model_dump() if v is not None else v for k, v in vreq.__dict__.items()}


@app.get("/query/with/<arg1>/path/<arg2>")
@validate(query=QueryModel)
def request_with_query_and_path_parameters(arg1: int, arg2: uuid.UUID):
    vreq = get_valid_request()
    return {k: v.model_dump() if v is not None else v for k, v in vreq.__dict__.items()}


@app.post("/body")
@validate(body=BodyModel)
def request_with_body():
    vreq = get_valid_request()
    return {k: v.model_dump() if v is not None else v for k, v in vreq.__dict__.items()}


@app.post("/form")
@validate(form=FormModel)
def request_with_form_data():
    vreq = get_valid_request()
    return {k: v.model_dump() if v is not None else v for k, v in vreq.__dict__.items()}


if __name__ == "__main__":
    app.run(debug=True)
