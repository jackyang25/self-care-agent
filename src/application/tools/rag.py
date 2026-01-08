"""RAG retrieval tool for knowledge base access."""

import logging
from typing import List, Optional

from langchain_core.tools import tool

from src.application.services.rag import search_documents
from src.application.tools.schemas.rag import RAGInput, RAGOutput
from src.shared.config import RAG_LIMIT_DEFAULT

logger = logging.getLogger(__name__)


@tool(args_schema=RAGInput, response_format="content_and_artifact")
def search_knowledge_base_tool(
    query: str,
    content_types: Optional[List[str]] = None,
    conditions: Optional[List[str]] = None,
    country: Optional[str] = None,
    limit: Optional[int] = RAG_LIMIT_DEFAULT,
) -> tuple[str, RAGOutput]:
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

    provide a clear, specific search query. optionally filter by content_types, conditions, or country for more targeted results.

    use when: you need clinical evidence or guidelines; patient asks about treatments or protocols; you need to verify medical information.

    safety boundaries:
    - retrieved content is informational guidance, not patient-specific diagnosis.
    - if the user reports symptoms, pair this with triage tools for urgency decisions.

    do not use for: patient-specific data; scheduling appointments; ordering commodities."""

    logger.info(
        f"Received args {{query={query[:50] + '...' if len(query) > 50 else query}, content_types={content_types}, conditions={conditions}, country={country}, limit={limit}}}"
    )

    try:
        results = search_documents(
            query=query,
            limit=limit,
            content_types=content_types,
            country_context_id=country,
            conditions=conditions,
        )

        if not results:
            logger.info("Completed {found=0, preview=[]}")
            output = RAGOutput(
                status="no_results",
                message="no relevant documents found",
                documents=[],
                query=query,
                count=0,
            )
            content_for_llm = (
                "No relevant documents found in the knowledge base for this query."
            )
            return (content_for_llm, output)

        # format results for LLM/agent consumption
        formatted_docs = []
        for doc in results:
            formatted_docs.append(
                {
                    "title": doc.title,
                    "content": doc.content,
                    "source": doc.source_name or "unknown",
                    "source_version": doc.source_version,
                    "similarity": round(doc.similarity, 3),
                    "content_type": doc.content_type,
                }
            )

        # log a lightweight preview of sources (avoid logging full document text)
        preview = [
            {
                "title": d.get("title"),
                "source": d.get("source"),
                "source_version": d.get("source_version"),
                "similarity": d.get("similarity"),
                "content_type": d.get("content_type"),
            }
            for d in formatted_docs[: min(3, len(formatted_docs))]
        ]
        logger.info(f"Completed {{found={len(results)}, preview={preview}}}")
        output = RAGOutput(
            message=f"found {len(results)} relevant document(s)",
            documents=formatted_docs,
            query=query,
            count=len(results),
        )

        # format documents for LLM to read and understand
        content_for_llm = f"Found {len(results)} relevant document(s):\n\n"
        for i, doc in enumerate(formatted_docs, 1):
            content_for_llm += f"[{i}] {doc['title']}\n"
            if doc.get("source"):
                content_for_llm += f"Source: {doc['source']}\n"
            if doc.get("similarity") is not None:
                content_for_llm += f"Similarity: {doc['similarity']}\n"
            content_for_llm += f"\n{doc['content']}\n\n"

        # Return (formatted content for LLM, structured artifact for extraction)
        return (content_for_llm.strip(), output)

    except Exception as e:
        output = RAGOutput(
            status="error",
            message=f"knowledge base search failed: {str(e)}",
            documents=[],
            query=query,
            count=0,
        )
        content_for_llm = f"Knowledge base search encountered an error: {str(e)}"
        return (content_for_llm, output)
