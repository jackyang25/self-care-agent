-- Create providers table and seed data
-- Run with: psql -d selfcare -f init-db/01_providers.sql

-- Create providers table
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
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Insert provider data
INSERT INTO providers (
    provider_id,
    external_provider_id,
    external_system,
    name,
    specialty,
    facility,
    available_days,
    country_context_id,
    contact_info,
    is_active,
    created_at,
    updated_at
) VALUES
    (
        '880e8400-e29b-41d4-a716-446655440000',
        NULL,
        NULL,
        'Dr. Sarah Smith',
        'cardiology',
        'Central Health Clinic',
        ARRAY['monday', 'wednesday', 'friday'],
        'us',
        '{"phone": "+12065551234", "email": "s.smith@centralhealthclinic.org"}'::jsonb,
        true,
        NOW(),
        NOW()
    ),
    (
        '880e8400-e29b-41d4-a716-446655440001',
        NULL,
        NULL,
        'Dr. James Chen',
        'pediatrics',
        'Children''s Health Center',
        ARRAY['tuesday', 'thursday', 'friday'],
        'us',
        '{"phone": "+12065552345", "email": "j.chen@childrenshealthcenter.org"}'::jsonb,
        true,
        NOW(),
        NOW()
    ),
    (
        '880e8400-e29b-41d4-a716-446655440002',
        NULL,
        NULL,
        'Dr. Maria Rodriguez',
        'general_practice',
        'Community Clinic',
        ARRAY['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
        'us',
        '{"phone": "+12065553456", "email": "m.rodriguez@communityclinic.org"}'::jsonb,
        true,
        NOW(),
        NOW()
    ),
    (
        '880e8400-e29b-41d4-a716-446655440003',
        NULL,
        NULL,
        'Dr. Aisha Ochieng',
        'obstetrics',
        'Maternal Health Center',
        ARRAY['monday', 'wednesday', 'thursday'],
        'ke',
        '{"phone": "+254701234567", "email": "a.ochieng@maternalhealthke.org"}'::jsonb,
        true,
        NOW(),
        NOW()
    ),
    (
        '880e8400-e29b-41d4-a716-446655440004',
        NULL,
        NULL,
        'Dr. Thabo Molefe',
        'general_practice',
        'Johannesburg Community Clinic',
        ARRAY['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
        'za',
        '{"phone": "+27115551234", "email": "t.molefe@jhbclinic.za"}'::jsonb,
        true,
        NOW(),
        NOW()
    )
ON CONFLICT (provider_id) DO NOTHING;
