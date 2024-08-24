# flask-request-check

Validate requests to a flask server using Pydantic models.

## Motivation

The purpose of Flask-Request-Check is to check (i.e. validate) requests against a [Pydantic](https://docs.pydantic.dev/latest/) model, and to implement this in the most straightforward way possible.

I had already begun implementing this before I saw that [Flask-Pydantic](https://github.com/bauerji/flask-pydantic) exists. Since it started as a small personal project I decided to continue with my own implementation, especially since Flask-Pydantic no longer works with the latest Pydantic 2.x. Nevertheless, this project is partly inspired by Flask-Pydantic.

## Installation

Not currently on PyPi. Clone the repo and then run the following:

```sh
pip install <path to flask-request-check>
```

For development, install the test dependencies - e.g.:

```sh
python -m pip install -e '.[dev]'
```

## Usage

The main steps for using this are:

- import the `validate` decorator
- write the representation classes using `Pydantic`
- access the validated data in the view function using the `get_valid_request` helper function.

For a full example of how to use this, see `example/app.py`.

### Path parameters

Simply type-hinting the Flask route function arguments will result in those parameters being validated:

```python
from flask_request-check.decoration import validate
from flask_request-check.valid_request import get_valid_request

...

@app.get("/path/typed/<a>/<b>/<c>/<d>")
@validate()  # Use the decorator
def valid_path(a: str, b: int, c: float, d: uuid.UUID):
    vreq = get_valid_request()
    return {k: v.model_dump() if v is not None else v for k, v in vreq.__dict__.items()}
```

If type hints are omitted, the fallback is to Flask's default - either converter types if specified in the path definition or strings.

### Query parameters

Query parameters require you to write a Pydantic model that represents the query parameters expected for the route. For example:

```python
from flask_request-check.decoration import validate
from flask_request-check.valid_request import get_valid_request
from pydantic import BaseModel


class QueryModel(BaseModel):
    a: str | None = None
    b: int | None = None
    c: float | None = None
    d: uuid.UUID | None = None
    arr: list[int] | None = None
    x: str

@app.get("/query")
@validate(query=QueryModel)
def request_with_query_parameters():
    vreq = get_valid_request()
    return {k: v.model_dump() if v is not None else v for k, v in vreq.__dict__.items()}
```

Note that most of these are optional, which is often the case for query parameters. However, we can of course require query parameters by simply defining the model field as required (see `QueryModel.x` above).

If no query model is given to the `@validate` decorator then no query parameters will be added to the valid request object. In that case they must be accessed normally via Flask's API.

### Body data

For request bodies we must define a model for what we expect, and then pass that class into the validate decorator:

```python
from flask_request-check.decoration import validate
from flask_request-check.valid_request import get_valid_request
from pydantic import BaseModel

class BodyModel(BaseModel):
    a: str
    b: int
    c: float
    d: uuid.UUID
    arr: list[int]

@app.post("/body")
@validate(body=BodyModel)
def request_with_body():
    vreq = get_valid_request()
    return {k: v.model_dump() if v is not None else v for k, v in vreq.__dict__.items()}
```

### Form data

Define a model for the form and then pass the class into the validate decorator:

```python
from flask_request-check.decoration import validate
from flask_request-check.valid_request import get_valid_request
from pydantic import BaseModel

class FormModel(BaseModel):
    a: str
    b: int

@app.post("/form")
@validate(form=FormModel)
def request_with_form_data():
    vreq = get_valid_request()
    return {k: v.model_dump() if v is not None else v for k, v in vreq.__dict__.items()}

```

## Contributing

pending

## License

MIT
