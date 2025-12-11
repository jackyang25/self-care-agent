"""create RAG tables and enable pgvector extension."""

import sys
from pathlib import Path

# add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import get_db_cursor


def create_rag_tables():
    """create RAG tables and enable pgvector extension."""
    print("setting up RAG infrastructure...")
    
    with get_db_cursor() as cur:
        # enable pgvector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        print("  ✓ enabled pgvector extension")
        
        # create documents table for storing knowledge base content
        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                content_type TEXT,
                metadata JSONB,
                embedding vector(1536),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
            )
        """)
        print("  ✓ created documents table")
        
        # create index for vector similarity search
        cur.execute("""
            CREATE INDEX IF NOT EXISTS documents_embedding_idx 
            ON documents 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """)
        print("  ✓ created vector similarity index")
        
        # create index for content type filtering
        cur.execute("""
            CREATE INDEX IF NOT EXISTS documents_content_type_idx 
            ON documents (content_type)
        """)
        print("  ✓ created content type index")
    
    print("✓ RAG infrastructure setup complete")


if __name__ == "__main__":
    create_rag_tables()

