import uuid

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base for response models that are built straight from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class TagRead(ORMModel):
    id: uuid.UUID
    name: str
