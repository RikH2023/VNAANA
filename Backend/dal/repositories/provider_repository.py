import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from Backend.dal.models import Provider


class ProviderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, provider_id: uuid.UUID) -> Provider | None:
        return self.db.get(Provider, provider_id)

    def get_by_domain(self, domain: str) -> Provider | None:
        return self.db.scalars(select(Provider).where(Provider.domain == domain)).first()

    def list_all(self) -> list[Provider]:
        return list(self.db.scalars(select(Provider).order_by(Provider.name)))

    def add(self, **fields: Any) -> Provider:
        provider = Provider(**fields)
        self.db.add(provider)
        self.db.flush()
        return provider
