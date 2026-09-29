import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Provider:
    id: uuid.UUID
    name: str
    domain: str
    country_code: str | None
    reliability_status: str
    created_at: datetime