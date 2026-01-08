"""RAG tool schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from .base import ToolResponse
from src.shared.config import RAG_LIMIT_DEFAULT

ALLOWED_RAG_CONTENT_TYPES: tuple[str, ...] = (
    "guideline",
    "protocol",
    "emergency",
    "algorithm",
    "reference",
)

ALLOWED_RAG_CONDITIONS: tuple[str, ...] = (
    "malaria",
    "depression",
    "fever",
    "hiv",
    "mental_health",
    "tb",
    "tuberculosis",
    "anxiety",
    "cardiac",
    "cardiovascular",
    "chest_pain",
    "cold",
    "contraception",
    "dehydration",
    "diabetes",
    "diarrhea",
    "family_planning",
    "flu",
    "headache",
    "hypertension",
    "meningitis",
    "pregnancy",
    "respiratory",
    "suicide",
)


class RAGInput(BaseModel):
    """input schema for RAG retrieval."""

    query: str = Field(
        description=(
            "retrieval query for the knowledge base. include the condition/topic + intent "
            "(e.g., self-care steps, monitoring, red flags, referral criteria) and, when relevant, "
            "the patient group and setting.\n"
            "example (good): 'type 2 diabetes self-care steps diet exercise monitoring red flags adult'\n"
            "example (too vague): 'diabetes'"
        )
    )
    content_types: Optional[List[str]] = Field(
        None,
        description=(
            f"optional filter by document category. allowed values: {', '.join(ALLOWED_RAG_CONTENT_TYPES)}. "
            "example: ['guideline', 'protocol']"
        ),
    )
    conditions: Optional[List[str]] = Field(
        None,
        description=(
            "optional filter by condition tags (controlled vocabulary). "
            f"allowed values: {', '.join(ALLOWED_RAG_CONDITIONS)}. "
            "example: ['diabetes'] or ['tb', 'hiv']. if unsure, omit this field."
        ),
    )
    country: Optional[str] = Field(
        None,
        description="country context for region-specific guidelines (e.g., 'za', 'ke')",
    )
    limit: Optional[int] = Field(
        RAG_LIMIT_DEFAULT,
        description="maximum number of documents to retrieve (default: RAG_LIMIT_DEFAULT)",
    )

    @field_validator("content_types")
    @classmethod
    def _normalize_and_validate_content_types(
        cls, value: Optional[List[str]]
    ) -> Optional[List[str]]:
        """Normalize and validate content_types against allowed values."""
        if value is None:
            return None

        normalized: List[str] = []
        for ct in value:
            if ct is None:
                continue
            s = ct.strip().lower()
            if not s:
                continue
            normalized.append(s)

        if not normalized:
            # treat empty/blank-only list as "no filter"
            return None

        allowed = set(ALLOWED_RAG_CONTENT_TYPES)
        invalid = sorted({ct for ct in normalized if ct not in allowed})
        if invalid:
            raise ValueError(
                f"invalid content_types: {invalid}. allowed values: {', '.join(ALLOWED_RAG_CONTENT_TYPES)}"
            )

        return normalized

    @field_validator("conditions")
    @classmethod
    def _normalize_conditions(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        """Normalize condition tags and keep only known values.

        Notes:
            - Converts spaces/hyphens to underscores to match stored tags (e.g., 'mental health' -> 'mental_health').
            - If all provided values are unknown after normalization, returns None (no filter) rather than hard-failing.
        """
        if value is None:
            return None

        allowed = set(ALLOWED_RAG_CONDITIONS)
        normalized: List[str] = []
        for cond in value:
            if cond is None:
                continue
            s = cond.strip().lower()
            if not s:
                continue
            s = s.replace("-", "_").replace(" ", "_")
            while "__" in s:
                s = s.replace("__", "_")

            # lightweight aliasing for common variants
            if "diabetes" in s and "diabetes" in allowed:
                s = "diabetes"
            elif (
                s in ("t2dm", "type2diabetes", "type_2_diabetes")
                and "diabetes" in allowed
            ):
                s = "diabetes"

            if s in allowed:
                normalized.append(s)

        if not normalized:
            return None

        # dedupe while preserving order
        deduped: List[str] = []
        seen = set()
        for s in normalized:
            if s not in seen:
                deduped.append(s)
                seen.add(s)

        return deduped


class RAGOutput(ToolResponse):
    """output model for rag retrieval tool."""

    message: str = Field(..., description="human-readable result message")
    documents: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="retrieved documents"
    )
    query: Optional[str] = Field(None, description="search query")
    count: Optional[int] = Field(None, description="number of results found")
