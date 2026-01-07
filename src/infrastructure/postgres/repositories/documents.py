"""document data access functions for RAG using ORM."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import or_, and_
from src.infrastructure.postgres.connection import get_db_session
from src.infrastructure.postgres.models import Document, Source


def insert_document(
    document_id: str,
    title: str,
    content: str,
    content_type: str,
    embedding: List[float],
    source_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    section_path: Optional[List[str]] = None,
    country_context_id: Optional[str] = None,
    conditions: Optional[List[str]] = None,
    metadata_json: Optional[str] = None,
) -> bool:
    """insert a document with embedding into database.

    args:
        document_id: unique document id
        title: document title
        content: document content
        content_type: content type classification (required)
        embedding: vector embedding
        source_id: optional reference to source document
        parent_id: optional reference to parent document (for chunked docs)
        section_path: hierarchical path (e.g., ["Symptoms", "Fever", "Red Flags"])
        country_context_id: country code (e.g., "za", "ke") or None for global
        conditions: list of medical conditions this document covers
        metadata_json: optional metadata as json string

    returns:
        True if successful, False otherwise
    """
    try:
        with get_db_session() as session:
            # check if document exists
            document = session.query(Document).filter(
                Document.document_id == UUID(document_id)
            ).first()
            
            if document:
                # update existing document
                document.source_id = UUID(source_id) if source_id else None
                document.parent_id = UUID(parent_id) if parent_id else None
                document.title = title
                document.content = content
                document.content_type = content_type
                document.section_path = section_path
                document.country_context_id = country_context_id
                document.conditions = conditions
                document.embedding = embedding
                document.metadata_ = metadata_json
            else:
                # create new document
                document = Document(
                    document_id=UUID(document_id),
                    source_id=UUID(source_id) if source_id else None,
                    parent_id=UUID(parent_id) if parent_id else None,
                    title=title,
                    content=content,
                    content_type=content_type,
                    section_path=section_path,
                    country_context_id=country_context_id,
                    conditions=conditions,
                    embedding=embedding,
                    metadata_=metadata_json,
                )
                session.add(document)
            
            return True
    except Exception:
        return False


def search_documents_by_embedding(
    query_embedding: List[float],
    limit: int = 5,
    content_type: Optional[str] = None,
    content_types: Optional[List[str]] = None,
    country_context_id: Optional[str] = None,
    conditions: Optional[List[str]] = None,
    include_global: bool = True,
) -> List[Dict[str, Any]]:
    """search for similar documents using vector similarity with filtering.

    args:
        query_embedding: query vector embedding
        limit: maximum number of results
        content_type: optional filter by single content type (deprecated, use content_types)
        content_types: optional filter by multiple content types
        country_context_id: optional filter by country (includes global docs if include_global=True)
        conditions: optional filter by medical conditions (matches any)
        include_global: whether to include global docs (country_context_id IS NULL)

    returns:
        list of document dicts with similarity scores
    """
    try:
        with get_db_session() as session:
            # build query with joins
            query = (
                session.query(
                    Document,
                    Source,
                    # calculate cosine similarity
                    (1 - Document.embedding.cosine_distance(query_embedding)).label("similarity")
                )
                .outerjoin(Source, Document.source_id == Source.source_id)
            )
            
            # apply filters
            filters = []
            
            # content type filtering
            if content_types:
                filters.append(Document.content_type.in_(content_types))
            elif content_type:
                filters.append(Document.content_type == content_type)
            
            # country filtering
            if country_context_id:
                if include_global:
                    filters.append(
                        or_(
                            Document.country_context_id == country_context_id,
                            Document.country_context_id.is_(None)
                        )
                    )
                else:
                    filters.append(Document.country_context_id == country_context_id)
            
            # conditions filtering (matches any condition in the list)
            if conditions:
                filters.append(Document.conditions.overlap(conditions))
            
            if filters:
                query = query.filter(and_(*filters))
            
            # order by similarity and limit
            results = (
                query.order_by(Document.embedding.cosine_distance(query_embedding))
                .limit(limit)
                .all()
            )
            
            output = []
            for document, source, similarity in results:
                doc_dict = {
                    "document_id": str(document.document_id),
                    "title": document.title,
                    "content": document.content,
                    "content_type": document.content_type,
                    "section_path": document.section_path,
                    "country_context_id": document.country_context_id,
                    "conditions": document.conditions,
                    "metadata": document.metadata,
                    "source_id": str(document.source_id) if document.source_id else None,
                    "source_name": source.name if source else None,
                    "source_version": source.version if source else None,
                    "similarity": float(similarity),
                }
                output.append(doc_dict)
            
            return output
    except Exception:
        return []


def delete_document(document_id: str) -> bool:
    """delete a document by ID.

    args:
        document_id: document uuid

    returns:
        True if document was deleted, False otherwise
    """
    try:
        with get_db_session() as session:
            document = session.query(Document).filter(
                Document.document_id == document_id
            ).first()
            
            if document:
                session.delete(document)
                return True
            return False
    except Exception:
        return False


def get_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """get document by document_id.

    args:
        document_id: document uuid

    returns:
        document dict or None if not found
    """
    try:
        with get_db_session() as session:
            result = (
                session.query(Document, Source)
                .outerjoin(Source, Document.source_id == Source.source_id)
                .filter(Document.document_id == document_id)
                .first()
            )
            
            if result:
                document, source = result
                return {
                    "document_id": str(document.document_id),
                    "title": document.title,
                    "content": document.content,
                    "content_type": document.content_type,
                    "section_path": document.section_path,
                    "country_context_id": document.country_context_id,
                    "conditions": document.conditions,
                    "metadata": document.metadata,
                    "source_id": str(document.source_id) if document.source_id else None,
                    "parent_id": str(document.parent_id) if document.parent_id else None,
                    "source_name": source.name if source else None,
                    "source_version": source.version if source else None,
                }
            return None
    except Exception:
        return None


def get_documents_by_source(source_id: str) -> List[Dict[str, Any]]:
    """get all documents from a specific source.

    args:
        source_id: source uuid

    returns:
        list of document dicts
    """
    try:
        with get_db_session() as session:
            documents = (
                session.query(Document)
                .filter(Document.source_id == source_id)
                .order_by(Document.section_path, Document.title)
                .all()
            )
            
            return [
                {
                    "document_id": str(doc.document_id),
                    "title": doc.title,
                    "content_type": doc.content_type,
                    "section_path": doc.section_path,
                    "country_context_id": doc.country_context_id,
                    "conditions": doc.conditions,
                    "metadata": doc.metadata,
                }
                for doc in documents
            ]
    except Exception:
        return []


def get_documents_by_condition(
    condition: str,
    country_context_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """get all documents related to a specific medical condition.

    args:
        condition: medical condition to search for
        country_context_id: optional filter by country

    returns:
        list of document dicts
    """
    try:
        with get_db_session() as session:
            query = session.query(Document).filter(
                Document.conditions.contains([condition])
            )
            
            if country_context_id:
                query = query.filter(
                    or_(
                        Document.country_context_id == country_context_id,
                        Document.country_context_id.is_(None)
                    )
                )
            
            documents = query.order_by(
                Document.content_type,
                Document.title
            ).all()
            
            return [
                {
                    "document_id": str(doc.document_id),
                    "title": doc.title,
                    "content_type": doc.content_type,
                    "section_path": doc.section_path,
                    "country_context_id": doc.country_context_id,
                    "conditions": doc.conditions,
                    "metadata": doc.metadata,
                }
                for doc in documents
            ]
    except Exception:
        return []
