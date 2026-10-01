import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from Backend.dal.models import Provider as ProviderModel
from Backend.Logic.domain.provider import Provider
from Backend.Logic.ports.provider_repository import (
    ProviderRepository as ProviderRepositoryPort,
)


class ProviderRepository(ProviderRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(provider: ProviderModel) -> Provider:
        return Provider(
            id=provider.id,
            name=provider.name,
            domain=provider.domain,
            country_code=provider.country_code,
            reliability_status=provider.reliability_status,
            created_at=provider.created_at,
        )

    def get(self, provider_id: uuid.UUID) -> Provider | None:
        provider = self.db.get(ProviderModel, provider_id)

        if provider is None:
            return None

        return self._to_domain(provider)

    def get_by_domain(self, domain: str) -> Provider | None:
        stmt = select(ProviderModel).where(
            ProviderModel.domain == domain
        )

        provider = self.db.scalars(stmt).first()

        if provider is None:
            return None

        return self._to_domain(provider)

    def list_all(self) -> list[Provider]:
        providers = self.db.scalars(
            select(ProviderModel).order_by(ProviderModel.name)
        )

        return [self._to_domain(provider) for provider in providers]

    def add(self, **fields: Any) -> Provider:
        provider_model = ProviderModel(**fields)

        self.db.add(provider_model)
        self.db.flush()

        return self._to_domain(provider_model)