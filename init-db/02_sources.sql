-- Create sources table and seed data
-- Run with: psql -d selfcare -f init-db/02_sources.sql

-- Create sources table for RAG document provenance
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
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Insert source data
INSERT INTO sources (
    source_id,
    name,
    source_type,
    country_context_id,
    version,
    url,
    publisher,
    effective_date,
    metadata,
    created_at,
    updated_at
) VALUES
    (
        '00000000-0000-0000-0000-000000000001',
        'Generic Self-Care Guidelines',
        'guideline',
        NULL,
        '1.0',
        NULL,
        'Global Health Initiative',
        '2024-01-01',
        '{"description": "General healthcare guidance applicable globally"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        '00000000-0000-0000-0000-000000000002',
        'Adult Primary Care 2023',
        'clinical_guideline',
        'za',
        '2023',
        'https://knowledgehub.health.gov.za/system/files/elibdownloads/2023-10/APC_2023_Clinical_tool-EBOOK.pdf',
        'South African National Department of Health',
        '2023-10-01',
        '{"country": "South Africa", "scope": "primary care", "target_audience": "healthcare workers"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        '00000000-0000-0000-0000-000000000003',
        'Kenya Essential Medicines List 2023',
        'formulary',
        'ke',
        '2023',
        'https://www.health.go.ke/wp-content/uploads/2023/06/KEML-2023.pdf',
        'Ministry of Health Kenya',
        '2023-06-01',
        '{"country": "Kenya", "scope": "essential medicines", "type": "national formulary"}'::jsonb,
        NOW(),
        NOW()
    )
ON CONFLICT (source_id) DO NOTHING;
