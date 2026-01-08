"""Test script to verify RAG functionality using ORM."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select, func
from src.application.services.rag import search_documents
from src.infrastructure.postgres.connection import get_db_session
from src.infrastructure.postgres.models import Document


def test_database_connection():
    """Test database connection using ORM."""
    print("=" * 80)
    print("Testing database connection...")
    print("=" * 80)
    try:
        with get_db_session() as session:
            count = session.query(func.count(Document.document_id)).scalar()
        print(f"✓ Database connected successfully")
        print(f"✓ Documents in database: {count}")
        return count > 0
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def test_document_samples():
    """Display sample documents from database using ORM."""
    print("\n" + "=" * 80)
    print("Sample documents in database...")
    print("=" * 80)
    try:
        with get_db_session() as session:
            docs = session.query(Document).limit(5).all()
            for doc in docs:
                has_embedding = "Yes" if doc.embedding is not None else "No"
                content_length = len(doc.content) if doc.content else 0
                print(
                    f"  • {doc.title} (type: {doc.content_type}, length: {content_length}, embedding: {has_embedding})"
                )
    except Exception as e:
        print(f"✗ Failed to fetch samples: {e}")


def test_vector_operations():
    """Test pgvector operations using ORM."""
    print("\n" + "=" * 80)
    print("Testing pgvector operations with ORM...")
    print("=" * 80)

    try:
        from src.application.services.rag import get_embedding

        with get_db_session() as session:
            # Check if documents with embeddings exist
            count = (
                session.query(func.count(Document.document_id))
                .filter(Document.embedding.isnot(None))
                .scalar()
            )

            if count > 0:
                print(f"✓ Found {count} documents with embeddings")
            else:
                print("✗ No documents with embeddings found")
                return False

            # Test vector search with ORM
            query_embedding = get_embedding("HIV testing")
            print(
                f"\n✓ Generated embedding for 'HIV testing' (dimension: {len(query_embedding)})"
            )

            # Use ORM's cosine_distance method
            similarity = (
                1 - Document.embedding.cosine_distance(query_embedding)
            ).label("similarity")
            query = (
                select(Document.title, Document.content_type, similarity)
                .where(Document.embedding.isnot(None))
                .order_by(Document.embedding.cosine_distance(query_embedding))
                .limit(5)
            )

            result = session.execute(query)
            docs = result.fetchall()

            if docs:
                print(f"\n✓ ORM Vector search WORKS! Found {len(docs)} results:")
                for i, doc in enumerate(docs, 1):
                    print(f"  [{i}] {doc.title}")
                    print(f"      Type: {doc.content_type}")
                    print(f"      Similarity: {doc.similarity:.3f}")
                return True
            else:
                print("✗ Vector search returned no results")
                return False

    except Exception as e:
        import traceback

        print(f"✗ Vector operations failed: {e}")
        print(traceback.format_exc())
        return False


def test_sqlalchemy_query():
    """Test SQLAlchemy vector query with ORM."""
    print("\n" + "=" * 80)
    print("Testing SQLAlchemy ORM vector query...")
    print("=" * 80)

    from src.application.services.rag import get_embedding

    query = "diabetes management"
    print(f"\nQuery: '{query}'")
    print("-" * 80)

    try:
        with get_db_session() as session:
            # Check document count
            count = session.query(Document).count()
            print(f"✓ Documents in database: {count}")

            if count == 0:
                print("✗ No documents found via ORM!")
                return

            # Generate embedding
            query_embedding = get_embedding(query)
            print(f"✓ Embedding generated (dimension: {len(query_embedding)})")

            # Run vector query using ORM
            results = (
                session.query(Document)
                .filter(Document.embedding.isnot(None))
                .order_by(Document.embedding.cosine_distance(query_embedding))
                .limit(3)
                .all()
            )

            if results:
                print(f"\n✓ Vector query returned {len(results)} results:")
                for i, doc in enumerate(results, 1):
                    print(f"  [{i}] {doc.title}")
                    print(f"      Type: {doc.content_type}")
                    print(f"      Content: {doc.content[:100]}...")
            else:
                print("✗ No results found")

    except Exception as e:
        import traceback

        print(f"✗ Failed: {e}")
        print(traceback.format_exc())


def test_repository_search():
    """Test ORM-based search through service layer."""
    print("\n" + "=" * 80)
    print("Testing search through service layer (ORM-based)...")
    print("=" * 80)

    query = "HIV testing"
    print(f"\nQuery: '{query}'")
    print("-" * 80)

    try:
        # Use service layer (which uses ORM repository)
        results = search_documents(query=query, limit=3, min_similarity=0.0)

        if results:
            print(f"✓ Search returned {len(results)} results:")
            for i, doc in enumerate(results, 1):
                print(f"\n  [{i}] {doc.title}")
                print(f"      Similarity: {doc.similarity:.3f}")
                print(f"      Type: {doc.content_type}")
        else:
            print("✗ No results from search")

    except Exception as e:
        import traceback

        print(f"✗ Failed: {e}")
        print(traceback.format_exc())


def test_rag_search():
    """Test RAG search functionality."""
    print("\n" + "=" * 80)
    print("Testing RAG search...")
    print("=" * 80)

    test_queries = [
        "HIV testing",
        "diabetes management",
        "pregnancy care",
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 80)
        try:
            # Try with lower similarity threshold
            results = search_documents(query=query, limit=3, min_similarity=0.0)

            if results:
                print(f"✓ Found {len(results)} document(s)")
                for i, doc in enumerate(results, 1):
                    print(f"\n  [{i}] {doc.title}")
                    print(f"      Similarity: {doc.similarity:.3f}")
                    print(f"      Type: {doc.content_type}")
                    print(f"      Content: {doc.content[:100]}...")
                    if doc.source_name:
                        print(f"      Source: {doc.source_name}")
            else:
                print(f"✗ No results found")
        except Exception as e:
            import traceback

            print(f"✗ Search failed: {e}")
            print(traceback.format_exc())


def main():
    """Run all ORM-based tests."""
    print("\n" + "=" * 80)
    print("RAG SYSTEM TEST (ORM-based)")
    print("=" * 80 + "\n")

    # Test database connection
    db_ok = test_database_connection()

    if not db_ok:
        print("\n⚠ No documents in database. Run 'make embeddings' to populate.")
        sys.exit(1)

    # Show sample documents
    test_document_samples()

    # Test vector operations with ORM
    test_vector_operations()

    # Test SQLAlchemy query
    test_sqlalchemy_query()

    # Test repository search
    test_repository_search()

    # Test RAG search (full pipeline)
    test_rag_search()

    print("\n" + "=" * 80)
    print("✓ All tests completed")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
