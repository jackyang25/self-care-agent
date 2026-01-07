"""RAG retrieval tool for knowledge base access."""

from typing import Dict, Any, List, Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from src.application.services.rag import search_documents
from src.shared.schemas.tools import RAGOutput


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


def rag_retrieval(
    query: str,
    content_type: Optional[str] = None,
    content_types: Optional[List[str]] = None,
    conditions: Optional[List[str]] = None,
    country: Optional[str] = None,
    limit: Optional[int] = 5,
) -> Dict[str, Any]:
    """search healthcare knowledge base using semantic search.

    args:
        query: search query for relevant documents
        content_type: filter by single content type
        content_types: filter by multiple content types
        conditions: filter by medical conditions
        country: country context for filtering (injected from context)
        limit: max documents to retrieve (default: 5)

    returns:
        dict with query results and formatted documents
    """

    try:
        results = search_documents(
            query=query,
            limit=limit,
            content_type=content_type,
            content_types=content_types,
            country_context_id=country,
            conditions=conditions,
        )

        if not results:
            return RAGOutput(
                status="no_results",
                message="no relevant documents found",
                documents=[],
            ).model_dump()

        # format results for LLM consumption
        formatted_docs = []
        for doc in results:
            formatted_docs.append(
                {
                    "title": doc.title,
                    "content": doc.content[:500],
                    "source": doc.source_name or "unknown",
                    "similarity": f"{doc.similarity:.2f}",
                }
            )

        return RAGOutput(
            message=f"found {len(results)} relevant document(s)",
            documents=formatted_docs,
            count=len(results),
        ).model_dump()

    except Exception as e:
        return RAGOutput(
            status="error",
            message=f"knowledge base search failed: {str(e)}",
            documents=[],
        ).model_dump()


rag_tool = StructuredTool.from_function(
    func=rag_retrieval,
    name="rag_knowledge_base",
    description="""search clinical knowledge base for evidence-based information.

use this tool when you need:
- clinical guidelines for specific conditions
- treatment protocols and recommendations  
- medication information and dosing
- evidence-based medical knowledge
- region-specific healthcare guidance

the knowledge base contains:
- WHO clinical guidelines
- national healthcare protocols
- medical reference materials
- treatment algorithms

provide a clear, specific search query. optionally filter by content_type, conditions, or country for more targeted results.

use when: you need clinical evidence or guidelines; patient asks about treatments or protocols; you need to verify medical information.

do not use for: patient-specific data; scheduling appointments; ordering commodities.""",
    args_schema=RAGInput,
)
