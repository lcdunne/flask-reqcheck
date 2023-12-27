# flask-reqcheck

Validate requests to a flask server using Pydantic models.

## Motivation

The purpose of Flask-Reqcheck is to check (i.e. validate) requests against a [Pydantic](https://docs.pydantic.dev/latest/) model, and to implement this in the most straightforward way possible.

I had already begun implementing this before I saw that [Flask-Pydantic](https://github.com/bauerji/flask-pydantic) exists. Since it started as a small personal project I decided to continue with my own implementation, especially since Flask-Pydantic no longer works with the latest Pydantic 2.x. Nevertheless, this project is partly inspired by Flask-Pydantic.

## Installation

Not currently on PyPi. Clone the repo and then run the following:

```python
pip install <path to flask-reqcheck>
```

## Usage

The main points for using this are:

- import the `validate` decorator
- write the representation classes using the `Pydantic` library
- access the validated data in the view function using the `request.query_params`, `request.path_params`, `request.body`, and `request.form_data`.

### Path parameters

```python
from flask_reqcheck import validate

@app.get("/<petId>")
@validate()
def get_by_id(petId: int):
  return {"path": request.path_params}

```

Simply type hinting the function arguments is sufficient for path parameters. This follows the Flask convention for having path parameters as the function arguments. Although we can specify converters in the path definition with `@app.get("/<int: petId>")` to convert `petId` from a string to an integer, by type hinting the argument itself the `validate()` call will automatically convert the value. However, to use the converted value, we must access it via `request.path_params` rather than directly with `petId`. This is subject to change in the future.

You may alternatively specify a path representation with Pydantic and pass it in as with the `@validate(path=MyPathRepresentation)`.

For query parameters, write a `Pydantic` class that represents the query valid parameters and their types. Specifically for query parameters, make sure that they can all default to `None`, since query parameters should always be optional:

```python
from pydantic import BaseModel


class PetStatus(BaseModel):
    # Query parameter model.
    status: str | None = None

@app.get("/findByStatus")
@validate(query=PetStatus)
def find_by_status():
    return {"query": request.query_params}
```

This will perform the necessary type conversion via `Pydantic`, and exposes the query parameters as a dictionary with `request.query_params`.

Posting a JSON body, or form data, also requires specifying a representation model:

```python
from pydantic import Field


class Pet(BaseModel):
    id: int
    name: str
    category: dict
    photo_urls: list[str] = Field(alias="photoUrls")
    tags: list[dict]
    status: str


class PetForm(BaseModel):
    name: str
    status: str

@app.post("/")
@validate(body=rpr.Pet)
def create_pet():
    return {"body": request.body}, 200


@app.post("/<petId>")
@validate(form=PetForm)
def update_pet_with_form(petId: int):
    print("Got here")
    return {"form": request.form_data, "path": request.path_params}
```

## Contributing

pending

## To-Do

- Handle query parameters:
  - list
  - multiple definition (see Pet Store's [findPetsByTags](https://petstore3.swagger.io/#/pet/findPetsByTags))

## License

MIT
