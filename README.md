# Flask-Reqcheck

**Flask-Reqcheck** lets you validate requests in your Flask applications. With a simple 
decorator and some [Pydantic](https://docs.pydantic.dev/latest/) models, you can quickly 
validate incoming request bodies, query parameters, and url path parameters, reducing 
boilerplate code and minimising errors.

## Installation

Run the following (preferably inside a virtual environment):

```sh
pip install flask-reqcheck
```

## Usage

Flask-Reqcheck is very straightforward to use. The main objects of interest are the `ReqCheck` extension class, the `@validate` decorator, and the `get_valid_request` function.

The `ReqCheck` extension is initialised like all other Flask extensions during the application setup (see example below). However it is only used for convenience to register a default 
validation error handler - it is not currently an essential step and can be skipped entirely in favour of your own error handler.

Initialise the extension:
```python

from flask import Flask
from flask_reqcheck import ReqCheck

app = Flask(__name__)
reqcheck = ReqCheck(app)
```

Or do that with the factory approach and lazy initialisation:

```python

from flask import Flask
from flask_reqcheck import ReqCheck

reqcheck = ReqCheck()

def init_app():
    app = Flask(__name__)
    reqcheck.init_app(app)
    ...
    return app()
```

The `validate` decorator is for annotating flask route functions. When you do this, you provide a Pydantic model for the components of the HTTP 
request that you would like to validate, such as `body`, `query`, `path`, etc. If the request inputs fail to match the corresponding model then 
a HTTP error is raised. 

Aside from `@validate`, you can use the more specific decorators - `@validate_body`, `@validate_form`, `@validate_path`, 
`@validate_query`, etc (see the API reference).

The `get_valid_request` is a helper function for use *within* the Flask route function. When using `@validate`, a new instance of the `ValidRequest` class 
will be created and stored for the current request context. We can use `get_valid_request` to retrieve that object and access its attributes, which correspond 
to the different HTTP components that were validated.

For example:

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

First, we import `validate` and `get_valid_request` from Flask-Reqcheck. Then we create a custom model using Pydantic’s `BaseClass` - in this example, it is a simple model for the expected request body. Then you annotate the Flask route function with `@validate`, providing our model of the request body. Finally, within our route function’s logic, we access the instance of the `ValidRequest` class and assign it to a variable using `vreq = get_valid_request()`. We could then call `print(vreq.body)` to obtain the instance of our request body model.

More specific decorators can also be used:
- `@validate_body`
- `@validate_form`
- `@validate_path`
- `@validate_query`

For a full example, see the [examples directory in the Flask-Reqcheck repository](/example/).

## Contributing

Clone the repo, pip install locally, then make the changes. Please do the following:

- Branch off of the `develop` branch to work on changes
- Use the `/feature/{feature name}` or `/bugfix/{bugfix name}` format for branch names
- PR from your branch into `develop`
- Use the [Black](https://black.readthedocs.io/en/stable/) formatter along with [isort](https://pycqa.github.io/isort/) to keep the codebase clean. Before making a PR:
    - `python -m black .`
    - `python -m isort .`
- Update the docs where necessary - the `make html` command from the `/docs` directory might be enough for minor changes. Otherwise, see how they are structured and make changes accordingly. Given that the focus is on just a few functions, the rest of the API is only documented in the code itself so it might not be necessary to include that in the main docs html.
- Use `numpy` style docstrings
- Write tests - PRs will fail if the tests fail


## License

MIT
