import representations as rpr
from error_handling import handle_errors_with_json
from flask import Blueprint, Flask, abort, request

from flask_reqcheck import validate

app = Flask(__name__)
pet = Blueprint("pet", __name__, url_prefix="/pet")


@pet.get("/findByStatus")
@validate(query=rpr.PetStatus)
def find_by_status():
    return {"query": request.query_params}


@pet.get("/findByTags")
@validate(query=rpr.PetStatus)
def find_by_tags():
    abort(404, "This page does not exist yet as it has not been implemented.")
    return {"query": request.query_params}


@pet.get("/<petId>")
@validate()
def get_by_id(petId: int):
    # Use via request.path_params instead of petId to ensure correct type
    # Or type-hint the <petId> with <int:petId> to use Flask converter
    # return {"path": request.path_params}
    return {"path": request.path_params}


@pet.post("/")
@validate(body=rpr.Pet)
def create_pet():
    return {"body": request.body}, 200


@pet.put("/")
@validate(body=rpr.Pet)
def update_existing_pet():
    return {"body": request.body}, 200


@pet.post("/<petId>")
@validate(form=rpr.PetForm)
def update_pet_with_form(petId: int):
    print("Got here")
    return {"form": request.form_data, "path": request.path_params}


app.register_blueprint(pet)

for code in [400, 401, 403, 404, 405, 415, 500]:
    app.register_error_handler(code, handle_errors_with_json)

if __name__ == "__main__":
    app.run()
