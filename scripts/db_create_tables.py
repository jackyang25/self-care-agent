"""create database tables if they don't exist."""

import sys
from pathlib import Path

# add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import get_db_cursor


def create_tables():
    """create all database tables."""
    print("creating database tables...")
    
    with get_db_cursor() as cur:
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
                demographics JSONB,
                accessibility JSONB,
                is_deleted BOOLEAN DEFAULT false,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
            )
        """)
        print("  ✓ created users table")
        
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
    
    print("✓ all tables created successfully")


if __name__ == "__main__":
    create_tables()

