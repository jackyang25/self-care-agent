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
                timezone TEXT DEFAULT 'UTC',
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
    
    print("✓ all tables created successfully")


if __name__ == "__main__":
    create_tables()

