"""create database tables if they don't exist."""

import sys
from pathlib import Path

# add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.persistence.postgres.connection import get_db_cursor


def create_tables():
    """create all database tables (app + RAG)."""
    print("creating database tables...")

    with get_db_cursor() as cur:
        # enable pgvector extension for RAG
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        print("  ✓ enabled pgvector extension")

        # create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id UUID PRIMARY KEY,
                fhir_patient_id TEXT,
                primary_channel TEXT,
                phone_e164 TEXT,
                email TEXT,
                preferred_language TEXT,
                literacy_mode TEXT,
                country_context_id TEXT NOT NULL,
                timezone TEXT DEFAULT 'UTC',
                demographics JSONB,
                accessibility JSONB,
                is_deleted BOOLEAN DEFAULT false,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
            )
        """)
        print("  ✓ created users table")

        # create sources table for RAG document provenance
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name TEXT NOT NULL,
                source_type TEXT NOT NULL,
                country_context_id TEXT,
                version TEXT,
                url TEXT,
                publisher TEXT,
                effective_date DATE,
                metadata JSONB,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
            )
        """)
        print("  ✓ created sources table")

        # create interactions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                interaction_id UUID PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(user_id),
                channel TEXT NOT NULL,
                input JSONB NOT NULL,
                protocol_invoked TEXT,
                protocol_version TEXT,
                triage_result JSONB,
                risk_level TEXT,
                recommendations JSONB,
                follow_up_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
            )
        """)
        print("  ✓ created interactions table")

        # create consents table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS consents (
                consent_id UUID PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(user_id),
                scope TEXT NOT NULL,
                status TEXT NOT NULL,
                version TEXT,
                jurisdiction TEXT,
                evidence JSONB,
                recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
            )
        """)
        print("  ✓ created consents table")

        # create providers table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS providers (
                provider_id UUID PRIMARY KEY,
                external_provider_id TEXT,
                external_system TEXT,
                name TEXT NOT NULL,
                specialty TEXT NOT NULL,
                facility TEXT,
                available_days TEXT[],
                country_context_id TEXT NOT NULL,
                contact_info JSONB,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
            )
        """)
        print("  ✓ created providers table")

        # create appointments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id UUID PRIMARY KEY,
                external_appointment_id TEXT,
                external_system TEXT,
                user_id UUID NOT NULL REFERENCES users(user_id),
                provider_id UUID REFERENCES providers(provider_id),
                specialty TEXT,
                appointment_date DATE,
                appointment_time TIME,
                status TEXT DEFAULT 'scheduled',
                reason TEXT,
                triage_interaction_id UUID REFERENCES interactions(interaction_id),
                consent_id UUID REFERENCES consents(consent_id),
                sync_status TEXT DEFAULT 'pending',
                last_synced_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
            )
        """)
        print("  ✓ created appointments table")

        # create documents table for RAG (enhanced schema)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                source_id UUID REFERENCES sources(source_id),
                parent_id UUID REFERENCES documents(document_id),
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                content_type TEXT NOT NULL,
                section_path TEXT[],
                country_context_id TEXT,
                conditions TEXT[],
                embedding vector(1536),
                metadata JSONB,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
            )
        """)
        print("  ✓ created documents table")

        # create vector similarity index
        cur.execute("""
            CREATE INDEX IF NOT EXISTS documents_embedding_idx 
            ON documents 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """)
        print("  ✓ created vector similarity index")

        # create content type index
        cur.execute("""
            CREATE INDEX IF NOT EXISTS documents_content_type_idx 
            ON documents (content_type)
        """)
        print("  ✓ created content type index")

        # create country context index for filtering
        cur.execute("""
            CREATE INDEX IF NOT EXISTS documents_country_idx 
            ON documents (country_context_id)
        """)
        print("  ✓ created country context index")

        # create conditions GIN index for array search
        cur.execute("""
            CREATE INDEX IF NOT EXISTS documents_conditions_idx 
            ON documents USING GIN (conditions)
        """)
        print("  ✓ created conditions index")

        # create section_path GIN index for hierarchy search
        cur.execute("""
            CREATE INDEX IF NOT EXISTS documents_section_path_idx 
            ON documents USING GIN (section_path)
        """)
        print("  ✓ created section path index")

        # create source_id index for joining
        cur.execute("""
            CREATE INDEX IF NOT EXISTS documents_source_idx 
            ON documents (source_id)
        """)
        print("  ✓ created source index")

    print("✓ all tables created successfully")


if __name__ == "__main__":
    create_tables()
