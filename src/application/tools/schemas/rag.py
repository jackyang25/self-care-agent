"""RAG tool schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .base import ToolResponse


class RAGInput(BaseModel):
    """input schema for RAG retrieval."""

    query: str = Field(
        description="search query for finding relevant clinical information, guidelines, or protocols"
    )
    content_type: Optional[str] = Field(
        None,
        description="filter by content type (e.g., 'guideline', 'protocol', 'medication_info')",
    )
    content_types: Optional[List[str]] = Field(
        None,
        description="filter by multiple content types (e.g., ['guideline', 'protocol'])",
    )
    conditions: Optional[List[str]] = Field(
        None,
        description="filter by medical conditions (e.g., ['fever', 'malaria', 'tb'])",
    )
    country: Optional[str] = Field(
        None,
        description="country context for region-specific guidelines (e.g., 'za', 'ke')",
    )
    limit: Optional[int] = Field(
        5, description="maximum number of documents to retrieve (default: 5)"
    )


class RAGOutput(ToolResponse):
    """output model for rag retrieval tool."""

    message: str = Field(..., description="human-readable result message")
    documents: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="retrieved documents")
    query: Optional[str] = Field(None, description="search query")
    count: Optional[int] = Field(None, description="number of results found")

