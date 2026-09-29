import uuid
from dataclasses import dataclass


@dataclass
class Tag:
    id: uuid.UUID
    name: str