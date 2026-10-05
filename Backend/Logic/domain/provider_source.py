from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class ProviderSource:
    id: UUID
    provider_id: UUID
    provider_name: str
    provider_domain: str

    name: str
    source_type: str
    url: str
    poll_interval_minutes: int
    is_active: bool

    configuration: dict[str, Any]