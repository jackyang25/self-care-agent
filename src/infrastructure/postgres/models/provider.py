"""provider model."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import Boolean, Text, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Provider(Base):
    """provider model representing healthcare providers."""
    
    __tablename__ = "providers"
    
    provider_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    external_provider_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    external_system: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    specialty: Mapped[str] = mapped_column(Text, nullable=False)
    facility: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    available_days: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True
    )
    country_context_id: Mapped[str] = mapped_column(Text, nullable=False)
    contact_info: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )
    
    def to_dict(self) -> dict:
        """convert model to dictionary."""
        return {
            "provider_id": str(self.provider_id),
            "name": self.name,
            "specialty": self.specialty,
            "facility": self.facility,
            "available_days": self.available_days,
            "country_context_id": self.country_context_id,
            "contact_info": self.contact_info,
        }
