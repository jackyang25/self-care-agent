"""RAG retrieval tool for knowledge base search."""

from typing import Optional, List, Dict, Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from src.application.services.rag import search_documents
from src.shared.context import current_user_country
from src.shared.logger import get_tool_logger, log_tool_call
from src.shared.schemas.tools import RAGOutput

logger = get_tool_logger("rag")


class RAGInput(BaseModel):
    """input schema for RAG retrieval."""

    query: str = Field(
        description="search query to find relevant knowledge base documents"
    )
    content_type: Optional[str] = Field(
        None,
        description="filter by single content type (e.g., 'protocol', 'guideline', 'symptom', 'emergency')",
    )
    content_types: Optional[List[str]] = Field(
        None,
        description="filter by multiple content types (e.g., ['protocol', 'guideline'])",
    )
    conditions: Optional[List[str]] = Field(
        None,
        description="filter by medical conditions (e.g., ['fever', 'malaria', 'tb'])",
    )
    limit: Optional[int] = Field(
        5, description="maximum number of documents to retrieve (default: 5)"
    )


def rag_retrieval(
    query: str,
    content_type: Optional[str] = None,
    content_types: Optional[List[str]] = None,
    conditions: Optional[List[str]] = None,
    limit: Optional[int] = 5,
) -> Dict[str, Any]:
    """search the knowledge base for relevant healthcare information.

    use this tool when:
    - user asks questions about symptoms, conditions, or treatments
    - you need to provide evidence-based information from healthcare protocols or guidelines
    - user asks "what should i know about X?" or "tell me about Y"
    - you need to augment your response with authoritative healthcare knowledge

    the tool searches a vector database of healthcare documents and returns the most
    relevant content based on semantic similarity. results are automatically filtered
    to prioritize the user's country-specific guidelines (e.g., SA clinical protocols
    for South African users) while also including global guidelines.

    content_types available:
    - symptom: entry points for symptom-based triage
    - condition: chronic condition information
    - algorithm: clinical decision trees/flowcharts
    - protocol: step-by-step clinical protocols
    - guideline: general management guidance
    - medication: drug info, dosing, prescriber levels
    - reference: helplines, tables, quick reference
    - emergency: red flags, urgent care criteria
    """
    # get user's country context for filtering
    country_context_id = current_user_country.get()

    log_tool_call(
        logger,
        "rag_retrieval",
        query=query,
        content_type=content_type,
        content_types=content_types,
        conditions=conditions,
        country_context_id=country_context_id,
        limit=limit,
    )

    try:
        results = search_documents(
            query=query,
            limit=limit,
            content_type=content_type,
            content_types=content_types,
            country_context_id=country_context_id,
            conditions=conditions,
            min_similarity=0.5,  # quality gate - filters very low similarity results
            include_global=True,  # always include global docs alongside country-specific
        )

        if not results:
            return {
                "status": "success",
                "query": query,
                "country_context": country_context_id,
                "results_count": 0,
                "documents": [],
            }

        # format results for agent consumption
        formatted_results = []
        for result in results:
            doc = {
                "title": result["title"],
                "content": result["content"],
                "content_type": result.get("content_type"),
                "similarity": round(result["similarity"], 3),
            }
            # include source info if available
            if result.get("source_name"):
                doc["source"] = result["source_name"]
                if result.get("source_version"):
                    doc["source"] += f" ({result['source_version']})"
            # include country context if specific to a country
            if result.get("country_context_id"):
                doc["country"] = result["country_context_id"]
            # include conditions if tagged
            if result.get("conditions"):
                doc["conditions"] = result["conditions"]
            formatted_results.append(doc)

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
protocols, guidelines, treatment recommendations, and medical knowledge. it automatically
prioritizes country-specific clinical guidelines for the user's region while also including
global guidelines.

available content_types for filtering:
- symptom: symptom-based triage entry points
- condition: chronic condition information
- algorithm: clinical decision trees
- protocol: step-by-step clinical protocols
- guideline: general management guidance
- medication: drug info and dosing
- reference: helplines and quick reference
- emergency: red flags and urgent care criteria

examples:
- user: "what are the symptoms of diabetes?" → use rag_retrieval with query about diabetes symptoms
- user: "how should i treat a fever?" → use rag_retrieval with query about fever treatment, content_types=["guideline", "protocol"]
- user asking about emergency signs → use rag_retrieval with content_types=["emergency"]

do not use for: user-specific data (use database_query instead), ordering medications, or scheduling appointments.""",
    args_schema=RAGInput,
)
