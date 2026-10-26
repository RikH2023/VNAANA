from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from Backend.Dal.models.base import Base


class EventWeight(Base):
    __tablename__ = "event_weights"

    event_type: Mapped[str] = mapped_column(String, primary_key=True)
    weight: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
