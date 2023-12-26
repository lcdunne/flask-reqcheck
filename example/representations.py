from pydantic import BaseModel, Field


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


class PetStatus(BaseModel):
    # Query parameter model.
    # All query parameters should have default None as they are not required
    status: str | None = None


class PetTags(BaseModel):
    # TODO: Needs a deserializing. Maybe as simple as json.loads(query_param)
    # TODO: Needs matching to example from pet store, which has a tag ID
    tags: list[str]
