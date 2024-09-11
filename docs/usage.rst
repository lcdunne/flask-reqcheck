Usage
=====

Flask-Reqcheck is very straightforward to use. The main objects of interest are the ``ReqCheck`` extension class, the ``@validate`` decorator, and the ``get_valid_request`` function.

The ``ReqCheck`` extension is initialised like all other Flask extensions during the application setup (see example below). However it is only used for convenience to register a default 
validation error handler - it is not currently an essential step and can be skipped entirely in favour of your own error handler.

Initialise the extension:

.. code-block:: python
    
    from flask import Flask
    from flask_reqcheck import ReqCheck

    app = Flask(__name__)
    reqcheck = ReqCheck(app)

Or do that with the factory approach and lazy initialisation:

.. code-block:: python

    from flask import Flask
    from flask_reqcheck import ReqCheck

    reqcheck = ReqCheck()

    def init_app():
        app = Flask(__name__)
        reqcheck.init_app(app)
        ...
        return app()

The ``validate`` decorator is for annotating flask route functions. When you do this, you provide a Pydantic model for the components of the HTTP 
request that you would like to validate, such as ``body``, ``query``, ``path``, etc. If the request inputs fail to match the corresponding model then 
a HTTP error is raised. 

Aside from ``@validate``, you can use the more specific decorators - ``@validate_body``, ``@validate_form``, ``@validate_path``, 
``@validate_query``, etc (see the API reference).

The ``get_valid_request`` is a helper function for use *within* the Flask route function. When using ``@validate``, a new instance of the ``ValidRequest`` class 
will be created and stored for the current request context. We can use ``get_valid_request`` to retrieve that object and access its attributes, which correspond 
to the different HTTP components that were validated.




For example:

.. code-block:: python

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

First, we import ``validate`` and ``get_valid_request`` from Flask-Reqcheck. Then we create a custom model using Pydantic's ``BaseClass`` - in this example, it is
a simple model for the expected request body. Then you annotate the Flask route function with ``@validate``, providing our model of the request body. Finally, 
within our route function's logic, we access the instance of the ``ValidRequest`` class and assign it to a variable using ``vreq = get_valid_request()``. We could then 
call ``print(vreq.body)`` to obtain the instance of our request body model.

For a full example, see the `examples directory in the Flask-Reqcheck repository <https://github.com/lcdunne/flask-reqcheck/tree/main/example>`_.


Path Parameters
----------------

Simply type-hinting the Flask route function arguments will result in those parameters being validated, and a Pydantic model is not required in this case (but of course
it is possible to use one):

.. code-block:: python

   @app.get("/path/typed/<a>/<b>/<c>/<d>")
   @validate()  # A model is not required for the path parameters
   def valid_path(a: str, b: int, c: float, d: uuid.UUID):
       vreq = get_valid_request()
       return vreq.as_dict()

If type hints are omitted from the route function signature then it just falls back to Flask's default `converter types <https://flask.palletsprojects.com/en/3.0.x/quickstart/#variable-rules>`_ (if provided in the path definition) or strings.

Query Parameters
----------------

Query parameters do require you to write a Pydantic model that represents the query parameters expected for the route.

Here is an example of using a query model:

.. code-block:: python

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

Note that most of these are defined as optional, which is often the case for query parameters. However, we can of course require 
query parameters by simply defining the model field as required (like `QueryModel.x` in the above).

If no query model is given to ``@validate`` decorator then no query parameters will be added to the valid request object. In that 
case they must be accessed normally via Flask's API.

Body Data
---------

For request bodies we must define a model for what we expect, and then pass that class into the validate decorator:

.. code-block:: python

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

Form Data
---------

Define a model for the form and then pass the class into the validate decorator:

.. code-block:: python

   class FormModel(BaseModel):
       a: str
       b: int

   @app.post("/form")
   @validate(form=FormModel)
   def request_with_form_data():
       vreq = get_valid_request()
       return vreq.to_dict()
