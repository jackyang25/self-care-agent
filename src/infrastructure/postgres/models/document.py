"""document model for RAG."""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlalchemy import ForeignKey, Text, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from .base import Base

if TYPE_CHECKING:
    from .source import Source


class Document(Base):
    """document model for RAG with vector embeddings."""
    
    __tablename__ = "documents"
    
    document_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    source_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sources.source_id"),
        nullable=True
    )
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("documents.document_id"),
        nullable=True
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(Text, nullable=False)
    section_path: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True
    )
    country_context_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    conditions: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True
    )
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        Vector(1536),
        nullable=True
    )
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # relationships
    source: Mapped[Optional["Source"]] = relationship(
        "Source",
        back_populates="documents"
    )
    
    def to_dict(self) -> dict:
        """convert model to dictionary."""
        return {
            "document_id": str(self.document_id),
            "source_id": str(self.source_id) if self.source_id else None,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "title": self.title,
            "content": self.content,
            "content_type": self.content_type,
            "section_path": self.section_path,
            "country_context_id": self.country_context_id,
            "conditions": self.conditions,
            "metadata": self.metadata_,
        }

