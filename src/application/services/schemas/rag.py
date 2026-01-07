"""RAG service output schema."""

from typing import List, Optional

from pydantic import BaseModel


class DocumentSearchResult(BaseModel):
    """single document from RAG search."""
    
    title: str
    content: str
    similarity: float
    source_name: Optional[str] = None
    source_version: Optional[str] = None
    content_type: Optional[str] = None
    country_context_id: Optional[str] = None
    conditions: Optional[List[str]] = None

