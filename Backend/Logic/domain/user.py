import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class User:
    id: uuid.UUID
    age_band: str | None
    language: str | None
    region: str | None
    preferences: dict[str, Any] | None
    analytics_consent: bool
    consent_updated_at: datetime | None