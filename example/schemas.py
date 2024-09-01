import uuid

from pydantic import BaseModel, ConfigDict


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
