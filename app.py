from flask import Flask, request
from pydantic import BaseModel, Field

from flask_reqcheck import validate


class PathModel(BaseModel):
    id: int
    msg: str


class UserModel(BaseModel):
    id: int


class QueryModel(BaseModel):
    x: int = Field(None)
    y: str = Field(None)


class BodyModel(BaseModel):
    # use .model_json_schema() to get OAPI compliant schema. It's not exactly right.
    body_param: str = Field(
        description="JSON body submitted via POST", alias="bodyParam"
    )


app = Flask(__name__)


@app.route("/")
@validate()
def nothing_to_validate():
    return {
        "path": request.path_params,
        "query": request.query_params,
        "body": request.body,
    }


@app.route("/users/<id>")
@validate(path=UserModel)
def users(id):
    return {
        "path": request.path_params,
        "query": request.query_params,
        "body": request.body,
    }


@app.route("/body", methods=["POST"])
@validate(body=BodyModel)
def body_validate():
    return {
        "path": request.path_params,
        "query": request.query_params,
        "body": request.body,
    }


@app.route("/query", methods=["GET"])
@validate(query=QueryModel)
def query_validate():
    return {
        "path": request.path_params,
        "query": request.query_params,
        "body": request.body,
    }


@app.route("/path/<id>/to/<msg>", methods=["GET"])
@validate(path=PathModel)
def path_validate(id, msg):
    return {
        "path": request.path_params,
        "query": request.query_params,
        "body": request.body,
    }


@app.route("/bq", methods=["GET", "POST"])
@validate(body=BodyModel, query=QueryModel)
def body_query_validate():
    return {
        "path": request.path_params,
        "query": request.query_params,
        "body": request.body,
    }


@app.route("/bp/<id>/<msg>", methods=["GET", "POST"])
@validate(body=BodyModel, path=PathModel)
def body_path_validate(id, msg):
    return {
        "path": request.path_params,
        "query": request.query_params,
        "body": request.body,
    }


@app.route("/qp/<id>/<msg>")
@validate(query=QueryModel, path=PathModel)
def query_path_validate(id, msg):
    return {
        "path": request.path_params,
        "query": request.query_params,
        "body": request.body,
    }


@app.route("/qpb/<id>/<msg>", methods=["GET", "POST"])
@validate(query=QueryModel, path=PathModel, body=BodyModel)
def query_path_body_validate(id, msg):
    return {
        "path": request.path_params,
        "query": request.query_params,
        "body": request.body,
    }


# -- Playing about
@app.route("/debug", methods=["GET", "POST"])
def debug():
    has_body = (
        "Content-Length" in request.headers or "Transfer-Encoding" in request.headers
    )
    return {"body": has_body}


if __name__ == "__main__":
    app.run()
