"""RAG retrieval tool for knowledge base search."""

from typing import Optional, Dict, Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from src.services.rag import search_documents
from src.utils.tool_helpers import get_tool_logger, log_tool_call
from src.schemas.tool_outputs import RAGOutput

logger = get_tool_logger("rag")


class RAGInput(BaseModel):
    """input schema for RAG retrieval."""

    query: str = Field(
        description="search query to find relevant knowledge base documents"
    )
    content_type: Optional[str] = Field(
        None,
        description="filter by content type (e.g., 'protocol', 'guideline', 'treatment')",
    )
    limit: Optional[int] = Field(
        3, description="maximum number of documents to retrieve (default: 3)"
    )


def rag_retrieval(
    query: str,
    content_type: Optional[str] = None,
    limit: Optional[int] = 3,
) -> Dict[str, Any]:
    """search the knowledge base for relevant healthcare information.

    use this tool when:
    - user asks questions about symptoms, conditions, or treatments
    - you need to provide evidence-based information from healthcare protocols or guidelines
    - user asks "what should i know about X?" or "tell me about Y"
    - you need to augment your response with authoritative healthcare knowledge

    the tool searches a vector database of healthcare documents and returns the most
    relevant content based on semantic similarity. use the retrieved information to
    provide accurate, context-aware responses.
    """
    log_tool_call(
        logger, "rag_retrieval", query=query, content_type=content_type, limit=limit
    )

    try:
        results = search_documents(
            query=query,
            limit=limit,
            content_type=content_type,
            min_similarity=0.5,  # quality gate - filters very low similarity results
        )

        if not results:
            return {
                "status": "success",
                "query": query,
                "results_count": 0,
                "documents": [],
            }

        # format results for agent consumption
        formatted_results = []
        for result in results:
            formatted_results.append(
                {
                    "title": result["title"],
                    "content": result["content"],
                    "content_type": result.get("content_type"),
                    "similarity": round(result["similarity"], 3),
                }
            )

        return RAGOutput(
            query=query,
            results_count=len(formatted_results),
            documents=formatted_results,
        ).model_dump()

    except Exception as e:
        logger.error(f"rag retrieval error: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"error retrieving documents: {str(e)}",
            "query": query,
            "results_count": 0,
            "documents": [],
        }


rag_tool = StructuredTool.from_function(
    func=rag_retrieval,
    name="rag_retrieval",
    description="""search the healthcare knowledge base for relevant information using semantic search.

use this tool when:
- user asks questions about symptoms, medical conditions, treatments, or healthcare protocols
- you need evidence-based information to answer health-related questions
- user asks "what should i know about X?" or requests information about a health topic
- you need to provide authoritative healthcare knowledge beyond general knowledge

the tool performs semantic search across a vector database of healthcare documents including
protocols, guidelines, treatment recommendations, and medical knowledge. it returns the most
relevant documents based on semantic similarity to the query.

examples:
- user: "what are the symptoms of diabetes?" → use rag_retrieval with query about diabetes symptoms
- user: "how should i treat a fever?" → use rag_retrieval with query about fever treatment
- user: "tell me about hypertension" → use rag_retrieval with query about hypertension

do not use for: user-specific data (use database_query instead), ordering medications, or scheduling appointments.""",
    args_schema=RAGInput,
)
