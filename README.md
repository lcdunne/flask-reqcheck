# Flask-Reqcheck

Validate requests to a flask server using Pydantic models.

## Motivation

The purpose of Flask-Reqcheck is to simply validate requests against a [Pydantic](https://docs.pydantic.dev/latest/) model. This is partly inspired by [Flask-Pydantic](https://github.com/bauerji/flask-pydantic), and supports Pydantic v2 and the latest version of Flask.

## Installation

Run the following (preferably inside a virtual environment):

```sh
pip install flask-reqcheck
```

For development, clone the repository and install it locally, along with the test dependencies:

```sh
python -m pip install -e '.[dev]'
```

## Usage

Here is an example of how to use this library:

```python
from flask_reqcheck import validate, get_valid_request
from pydantic import BaseModel

# Write a class (with Pydantic) to represent the expected data
class BodyModel(BaseModel):
    a: str
    b: int
    c: float
    d: uuid.UUID
    arr: list[int]


@app.post("/body")
@validate(body=BodyModel)  # Decorate the view function
def request_with_body():
    vreq = get_valid_request()  # Access the validated data
    return vreq.to_dict()
```

First, import the `validate` decorator function and the `get_valid_request` helper function. The `validate` decorator accepts arguments in the form of Pydantic model classes for the request body, query parameters, path (url) parameters, and form data (headers & cookies not yet implemented). The `get_valid_request` function provides access to a `ValidRequest` object that stores the validated request data in a single place. Using this we can easily access our validated data from that object in our route functions.

For a full example of how to use this, see `example/app.py`.

### Path parameters

Simply type-hinting the Flask route function arguments will result in those parameters being validated, and a Pydantic model is not required in this case:

```python

@app.get("/path/typed/<a>/<b>/<c>/<d>")
@validate()  # A model is not required for the path parameters
def valid_path(a: str, b: int, c: float, d: uuid.UUID):
    vreq = get_valid_request()
    return vreq.as_dict()
```

If type hints are omitted from the route function signature then it just falls back to Flask's default - [converter types](https://flask.palletsprojects.com/en/3.0.x/quickstart/#variable-rules) (if provided in the path definition) or strings.

### Query parameters

Query parameters require you to write a Pydantic model that represents the query parameters expected for the route. For example:

```python
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
    return vreq.to_dict()
```

Note that most of these are defined as optional, which is often the case for query parameters. However, we can of course require query parameters by simply defining the model field as required (like `QueryModel.x` in the above).

If no query model is given to the `@validate` decorator then no query parameters will be added to the valid request object. In that case they must be accessed normally via Flask's API.

### Body data

For request bodies we must define a model for what we expect, and then pass that class into the validate decorator:

```python
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
    return vreq.to_dict()
```

### Form data

Define a model for the form and then pass the class into the validate decorator:

```python
class FormModel(BaseModel):
    a: str
    b: int

@app.post("/form")
@validate(form=FormModel)
def request_with_form_data():
    vreq = get_valid_request()
    return vreq.to_dict()

```

## Contributing

pending...

## License

MIT
