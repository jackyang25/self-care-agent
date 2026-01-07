"""source model for RAG document provenance."""

from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlalchemy import Text, Date, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .document import Document


class Source(Base):
    """source model for RAG document provenance."""
    
    __tablename__ = "sources"
    
    source_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(Text, nullable=False)
    country_context_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publisher: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )
    
    # relationships
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="source",
        lazy="selectin"
    )
    
    def to_dict(self) -> dict:
        """convert model to dictionary."""
        return {
            "source_id": str(self.source_id),
            "name": self.name,
            "source_type": self.source_type,
            "country_context_id": self.country_context_id,
            "version": self.version,
            "url": self.url,
            "publisher": self.publisher,
            "effective_date": str(self.effective_date) if self.effective_date else None,
            "metadata": self.metadata_,
            "created_at": str(self.created_at),
        }

