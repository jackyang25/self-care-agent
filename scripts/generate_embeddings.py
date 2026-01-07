"""Generate embeddings for documents that don't have them yet.

This script finds all documents with NULL embeddings and generates them
using OpenAI's embedding API. Run this after seeding documents via SQL.

Usage:
    python scripts/generate_embeddings.py
"""

import sys
from pathlib import Path

# add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.postgres.connection import get_db_session
from src.infrastructure.postgres.models import Document
from src.application.services.rag import get_embedding


def generate_missing_embeddings():
    """Find documents without embeddings and generate them."""
    
    print("Searching for documents without embeddings...")
    
    with get_db_session() as session:
        # Find all documents with NULL embedding
        docs_without_embeddings = session.query(Document).filter(
            Document.embedding.is_(None)
        ).all()
        
        if not docs_without_embeddings:
            print("All documents already have embeddings!")
            return
        
        total = len(docs_without_embeddings)
        print(f"Found {total} document(s) without embeddings")
        print()
        
        success_count = 0
        error_count = 0
        
        for i, doc in enumerate(docs_without_embeddings, 1):
            try:
                print(f"[{i}/{total}] Generating embedding for: {doc.title}")
                
                # Call OpenAI to generate embedding
                embedding = get_embedding(doc.content)
                
                # Update the document
                doc.embedding = embedding
                session.commit()
                
                print(f"  Success (embedding dimension: {len(embedding)})")
                success_count += 1
                
            except Exception as e:
                print(f"  Error: {e}")
                error_count += 1
                session.rollback()
        
        print()
        print("=" * 60)
        print(f"Generated {success_count} embedding(s)")
        if error_count > 0:
            print(f"Failed: {error_count} embedding(s)")
        print("=" * 60)


if __name__ == "__main__":
    try:
        generate_missing_embeddings()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

