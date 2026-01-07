"""RAG retrieval tool for knowledge base access."""

from typing import List, Optional

from langchain_core.tools import tool

from src.application.services.rag import search_documents
from src.application.tools.schemas.rag import RAGInput, RAGOutput


@tool(args_schema=RAGInput)
def rag_tool(
    query: str,
    content_type: Optional[str] = None,
    content_types: Optional[List[str]] = None,
    conditions: Optional[List[str]] = None,
    country: Optional[str] = None,
    limit: Optional[int] = 5,
) -> RAGOutput:
    """search clinical knowledge base for evidence-based information.

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

do not use for: patient-specific data; scheduling appointments; ordering commodities."""

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
                query=query,
                count=0,
            )

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
            query=query,
            count=len(results),
        )

    except Exception as e:
        return RAGOutput(
            status="error",
            message=f"knowledge base search failed: {str(e)}",
            documents=[],
            query=query,
            count=0,
        )
