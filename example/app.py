import uuid

from flask import Flask
from pydantic import BaseModel, ConfigDict

from flask_reqcheck import get_valid_request, validate, validate_path, validate_query

app = Flask(__name__)
setattr(app.json, "sort_keys", False)


class PathModel(BaseModel):
    a: str
    b: int
    c: int
    d: uuid.UUID


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

    model_config = ConfigDict(extra="forbid")


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
    return vreq.to_dict()


@app.get("/path/partially_typed/<a>/<b>/<c>/<d>")
@validate()
def valid_partially_typed_path(a, b: int, c: float, d):
    vreq = get_valid_request()
    return vreq.to_dict()


@app.get("/path/typed/<a>/<b>/<c>/<d>")
@validate()
def valid_path(a: str, b: int, c: float, d: uuid.UUID):
    vreq = get_valid_request()
    return vreq.to_dict()


@app.get("/query")
@validate(query=QueryModel)
def request_with_query_parameters():
    vreq = get_valid_request()
    return vreq.to_dict()


@app.get("/query/with/path/<a>/<b>/<c>/<d>")
@validate_path(path=PathModel)
@validate_query(query=QueryModel)
def request_with_query_and_path_parameters(a, b, c, d):
    vreq = get_valid_request()
    return vreq.to_dict()


@app.post("/body")
@validate(body=BodyModel)
def request_with_body():
    vreq = get_valid_request()
    return vreq.to_dict()


@app.post("/form")
@validate(form=FormModel)
def request_with_form_data():
    vreq = get_valid_request()
    return vreq.to_dict()


if __name__ == "__main__":
    app.run(debug=True)
