-- Create documents table and seed data (without embeddings)
-- Embeddings will be generated separately via Python script
-- Run with: psql -d selfcare -f init-db/03_documents.sql

-- Enable pgvector extension for vector embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table for RAG
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
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS documents_embedding_idx 
ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS documents_content_type_idx 
ON documents (content_type);

CREATE INDEX IF NOT EXISTS documents_country_idx 
ON documents (country_context_id);

CREATE INDEX IF NOT EXISTS documents_conditions_idx 
ON documents USING GIN (conditions);

CREATE INDEX IF NOT EXISTS documents_section_path_idx 
ON documents USING GIN (section_path);

CREATE INDEX IF NOT EXISTS documents_source_idx 
ON documents (source_id);

-- Insert document data (embeddings will be NULL initially)
INSERT INTO documents (
    document_id,
    title,
    content,
    content_type,
    source_id,
    parent_id,
    section_path,
    country_context_id,
    conditions,
    metadata_,
    created_at,
    updated_at
) VALUES
    (
        'doc-0000-0000-0000-0000-000000000000',
        'Fever Management Guidelines',
        'Fever is a common symptom that indicates the body is fighting an infection.

For adults with fever:
- Rest and stay hydrated by drinking plenty of fluids
- Take acetaminophen (paracetamol) or ibuprofen to reduce fever and discomfort
- Monitor temperature regularly
- Seek medical attention if fever persists for more than 3 days, exceeds 39.4°C (103°F), or is accompanied by severe symptoms like difficulty breathing, chest pain, or confusion

For children with fever:
- Ensure adequate fluid intake
- Use age-appropriate fever reducers (acetaminophen or ibuprofen) following dosage guidelines
- Seek immediate medical attention if child is under 3 months with any fever, or if fever is above 40°C (104°F)
- Watch for signs of dehydration or unusual behavior',
        'guideline',
        '00000000-0000-0000-0000-000000000001',
        NULL,
        ARRAY['Symptoms', 'Fever'],
        NULL,
        ARRAY['fever'],
        '{"category": "symptom_management"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0001-0000-0000-0000-000000000001',
        'Fever - Red Flags (South Africa)',
        'URGENT REFERRAL REQUIRED if fever with any of the following:

- Neck stiffness or photophobia (meningitis signs)
- Petechial or purpuric rash
- Altered mental status or confusion
- Severe respiratory distress
- Signs of shock (cold extremities, weak pulse, low BP)
- Unable to drink or retain fluids
- Recent travel to malaria-endemic area

In South Africa, consider:
- Malaria in febrile patients from endemic areas (Limpopo, Mpumalanga, KwaZulu-Natal)
- TB in patients with fever >2 weeks, night sweats, weight loss
- HIV-associated opportunistic infections

Refer to nearest facility with emergency services if danger signs present.',
        'emergency',
        '00000000-0000-0000-0000-000000000002',
        NULL,
        ARRAY['Symptoms', 'Fever', 'Red Flags'],
        'za',
        ARRAY['fever', 'malaria', 'meningitis'],
        '{"category": "emergency", "page_ref": "APC 2023"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0002-0000-0000-0000-000000000002',
        'Chest Pain Red Flags',
        'Chest pain can be a sign of serious medical conditions and requires immediate evaluation in certain situations.

Red flag symptoms requiring immediate emergency care:
- Severe chest pain that radiates to arm, neck, or jaw
- Chest pain accompanied by shortness of breath, sweating, or nausea
- Chest pain in someone with known heart disease or risk factors
- Chest pain that worsens with exertion
- Chest pain with dizziness or fainting

If experiencing any red flag symptoms, seek emergency medical care immediately. Do not delay.

For non-urgent chest pain:
- Rest and avoid activities that trigger the pain
- Monitor symptoms and note any changes
- Consider evaluation within 24-48 hours if symptoms persist or worsen',
        'emergency',
        '00000000-0000-0000-0000-000000000001',
        NULL,
        ARRAY['Symptoms', 'Chest Pain', 'Red Flags'],
        NULL,
        ARRAY['chest_pain', 'cardiac'],
        '{"category": "emergency"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0003-0000-0000-0000-000000000003',
        'Common Cold and Flu Management',
        'The common cold and influenza (flu) are viral respiratory infections. While similar, flu symptoms are typically more severe.

Self-care for cold and flu:
- Rest and allow your body to recover
- Stay hydrated with water, herbal teas, or clear broths
- Use saline nasal sprays or rinses for congestion
- Gargle with warm salt water for sore throat
- Use humidifier or steam to ease breathing
- Over-the-counter medications can help with symptoms
- Wash hands frequently to prevent spread

When to seek medical care:
- Symptoms persist beyond 10 days
- High fever (above 38.9°C or 102°F) that doesn''t respond to treatment
- Difficulty breathing or chest pain
- Persistent cough with colored mucus',
        'guideline',
        '00000000-0000-0000-0000-000000000001',
        NULL,
        ARRAY['Symptoms', 'Respiratory'],
        NULL,
        ARRAY['cold', 'flu', 'respiratory'],
        '{"category": "symptom_management"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0004-0000-0000-0000-000000000004',
        'Headache Management',
        'Headaches are common and most are not serious. However, certain symptoms require immediate medical attention.

Self-care for common headaches:
- Rest in a quiet, dark room
- Apply cold or warm compress to head or neck
- Stay hydrated
- Take over-the-counter pain relievers (paracetamol or ibuprofen)
- Practice relaxation techniques
- Avoid known triggers (stress, certain foods, lack of sleep)

Red flags requiring immediate medical attention:
- Sudden, severe headache (thunderclap headache)
- Headache after head injury
- Headache with fever, stiff neck, confusion, or vision changes
- New headache pattern in people over 50
- Headache that worsens despite treatment',
        'guideline',
        '00000000-0000-0000-0000-000000000001',
        NULL,
        ARRAY['Symptoms', 'Headache'],
        NULL,
        ARRAY['headache'],
        '{"category": "symptom_management"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0005-0000-0000-0000-000000000005',
        'Diarrhea and Dehydration Management',
        'Diarrhea is common and usually resolves within a few days. The main concern is preventing dehydration.

Self-care for diarrhea:
- Drink plenty of fluids (water, oral rehydration solution, clear broths)
- Avoid milk products temporarily
- Eat bland foods when able (rice, bananas, toast)
- Avoid caffeine, alcohol, and fatty foods
- Rest and allow body to recover

Oral rehydration solution (ORS):
- Available at pharmacies or can be made at home
- Essential for replacing lost fluids and electrolytes
- Give frequently in small amounts

Signs of dehydration requiring medical attention:
- Very dark urine or no urination for 8+ hours
- Extreme thirst, dry mouth and lips
- Dizziness, sunken eyes, confusion or weakness

Seek immediate care if diarrhea lasts more than 3 days, severe abdominal pain, blood in stool, or high fever.',
        'guideline',
        '00000000-0000-0000-0000-000000000001',
        NULL,
        ARRAY['Symptoms', 'Gastrointestinal'],
        NULL,
        ARRAY['diarrhea', 'dehydration'],
        '{"category": "symptom_management"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0006-0000-0000-0000-000000000006',
        'HIV Prevention and Testing',
        'HIV (Human Immunodeficiency Virus) can be prevented and managed effectively with modern treatments.

Prevention methods:
- Consistent and correct condom use
- Pre-exposure prophylaxis (PrEP) for high-risk individuals
- Post-exposure prophylaxis (PEP) within 72 hours of potential exposure
- Use of sterile needles (never share)
- Treatment as prevention: People living with HIV who maintain undetectable viral loads cannot transmit HIV sexually (U=U)

Testing:
- Regular testing is important for sexually active individuals
- Confidential and often free testing available at clinics
- Rapid tests provide results in 20 minutes
- Window period: HIV may not show on test for 3 months after exposure

If you test positive:
- HIV is a manageable chronic condition with treatment
- Antiretroviral therapy (ART) allows people to live long, healthy lives
- Early treatment is crucial
- Treatment prevents transmission to others',
        'protocol',
        '00000000-0000-0000-0000-000000000001',
        NULL,
        ARRAY['Chronic Conditions', 'HIV'],
        NULL,
        ARRAY['hiv'],
        '{"category": "sexual_health"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0007-0000-0000-0000-000000000007',
        'HIV Testing and Counselling (South Africa)',
        'HIV Testing Services (HTS) in South Africa follow the 2023 National HIV Testing Services Policy.

Who should test:
- Everyone at least once in their lifetime
- Sexually active individuals annually
- Pregnant women at first antenatal visit and again in third trimester
- TB patients at diagnosis
- STI patients
- Partners of PLHIV

Testing approach:
- Provider-initiated testing and counselling (PITC) recommended
- Self-testing available at pharmacies and clinics
- Rapid test algorithm: First test positive → confirmatory test

PrEP eligibility (2021 Guidelines):
- HIV-negative individuals at substantial risk
- Available at primary healthcare facilities
- Adolescent girls and young women priority population

PEP must be started within 72 hours of exposure.

Helplines:
- National AIDS Helpline: 0800 012 322 (24 hours)
- Right to Care: 082 957 6698',
        'protocol',
        '00000000-0000-0000-0000-000000000002',
        NULL,
        ARRAY['Chronic Conditions', 'HIV', 'Testing'],
        'za',
        ARRAY['hiv'],
        '{"category": "sexual_health", "policy_ref": "National HIV Testing Services Policy 2023"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0008-0000-0000-0000-000000000008',
        'Tuberculosis (TB) Screening and Testing',
        'Tuberculosis (TB) is a bacterial infection that primarily affects the lungs. It is curable with proper treatment.

Common symptoms (screen positive if ANY present):
- Persistent cough lasting more than 2 weeks
- Coughing up blood or mucus
- Chest pain
- Unexplained weight loss
- Night sweats
- Fever

Who should get tested:
- Anyone with symptoms listed above
- Close contacts of people with TB
- People living with HIV
- Healthcare workers
- People with weakened immune systems

Treatment:
- TB is curable with 6-9 months of antibiotics
- Must complete full course of treatment
- Never stop treatment early, even if feeling better
- Incomplete treatment can lead to drug-resistant TB',
        'protocol',
        '00000000-0000-0000-0000-000000000001',
        NULL,
        ARRAY['Chronic Conditions', 'TB'],
        NULL,
        ARRAY['tuberculosis', 'tb'],
        '{"category": "infectious_disease"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0009-0000-0000-0000-000000000009',
        'TB Screening Algorithm (South Africa)',
        'TB Screening per SA TB Screening and Testing SOP (June 2022):

Screen ALL patients at EVERY visit with these 4 questions:
1. Current cough of any duration?
2. Unexplained weight loss?
3. Drenching night sweats?
4. Fever?

If ANY symptom present → TB presumptive → Request sputum for GeneXpert

Additional screening for PLHIV:
- Ask about TB contact in household
- Check for enlarged lymph nodes

GeneXpert (Xpert MTB/RIF Ultra):
- First-line diagnostic test
- Detects TB and rifampicin resistance
- Results available same day
- If positive, initiate treatment immediately

TPT (TB Preventive Therapy):
- All PLHIV who screen negative for TB symptoms
- Child contacts of TB cases
- 3HP regimen (3 months isoniazid + rifapentine) preferred

Notification: All TB cases must be reported to District TB Coordinator.',
        'algorithm',
        '00000000-0000-0000-0000-000000000002',
        NULL,
        ARRAY['Chronic Conditions', 'TB', 'Screening'],
        'za',
        ARRAY['tuberculosis', 'tb'],
        '{"category": "infectious_disease", "policy_ref": "TB Screening and Testing SOP June 2022"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0010-0000-0000-0000-000000000010',
        'Contraception Methods',
        'Various contraception methods are available to prevent pregnancy.

Short-acting methods:
- Condoms: 85-98% effective, also prevent STIs
- Birth control pills: 91-99% effective with consistent use
- Emergency contraception: Up to 5 days after unprotected sex

Long-acting reversible methods (LARC):
- Intrauterine devices (IUDs): 99% effective, lasts 3-10 years
- Contraceptive implant: 99% effective, lasts 3-5 years
- Injectable contraceptives: 94-99% effective, every 3 months

Dual protection:
- Using condoms plus another method
- Protects against both pregnancy and STIs

Emergency contraception:
- Available without prescription in many countries
- Most effective when taken as soon as possible
- Does not cause abortion or affect future fertility',
        'guideline',
        '00000000-0000-0000-0000-000000000001',
        NULL,
        ARRAY['Women''s Health', 'Contraception'],
        NULL,
        ARRAY['contraception', 'family_planning'],
        '{"category": "sexual_health"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0011-0000-0000-0000-000000000011',
        'Pregnancy Warning Signs',
        'Most pregnancies progress normally, but certain symptoms require immediate medical attention.

Seek immediate medical care for:
- Vaginal bleeding or spotting
- Severe abdominal pain or cramping
- Severe headache or vision changes
- Sudden swelling of face, hands, or feet
- Fever over 38°C (100.4°F)
- Decreased or no fetal movement (after 20 weeks)
- Fluid leaking from vagina
- Signs of preterm labor (regular contractions before 37 weeks)

Danger signs in late pregnancy:
- Water breaking before 37 weeks
- Severe and persistent headache with vision problems
- Upper abdominal pain
- Rapid weight gain or severe swelling

Routine prenatal care:
- Regular checkups as scheduled
- Take prenatal vitamins with folic acid
- Avoid alcohol, tobacco, and recreational drugs',
        'emergency',
        '00000000-0000-0000-0000-000000000001',
        NULL,
        ARRAY['Women''s Health', 'Pregnancy', 'Warning Signs'],
        NULL,
        ARRAY['pregnancy'],
        '{"category": "maternal_health"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0012-0000-0000-0000-000000000012',
        'Mental Health and Stress Management',
        'Mental health is as important as physical health.

Signs you may need support:
- Persistent sadness or low mood for more than 2 weeks
- Loss of interest in activities you usually enjoy
- Changes in sleep or appetite
- Difficulty concentrating
- Feeling overwhelmed or unable to cope
- Thoughts of self-harm or suicide

Stress management techniques:
- Regular physical activity
- Adequate sleep (7-9 hours for adults)
- Deep breathing exercises and meditation
- Talking to trusted friends or family
- Setting realistic goals and boundaries

When to seek professional help:
- Symptoms interfere with daily life
- Thoughts of self-harm or suicide
- Using alcohol or drugs to cope

Emergency: If you or someone you know is in crisis, contact emergency services or a crisis helpline immediately.',
        'guideline',
        '00000000-0000-0000-0000-000000000001',
        NULL,
        ARRAY['Mental Health'],
        NULL,
        ARRAY['mental_health', 'depression', 'anxiety'],
        '{"category": "mental_health"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0013-0000-0000-0000-000000000013',
        'Mental Health Support (South Africa)',
        'Mental health conditions are common and treatable. Stigma-free care is your right.

Screening at PHC level:
- Ask about mood, sleep, appetite, concentration
- Use PHQ-2/PHQ-9 for depression screening
- Screen for suicidal ideation in all patients with low mood

Referral criteria:
- Active suicidal ideation with plan → Emergency
- Psychotic symptoms → Urgent psychiatric referral
- Severe depression not responding to treatment → Psychiatric referral

Treatment at PHC:
- Fluoxetine 20mg daily (first-line for depression)
- Amitriptyline 25-75mg nocte (alternative, also helps with pain)
- Counselling and psychosocial support

Helplines (South Africa):
- Suicide Crisis Line: 0800 567 567 (8am-8pm) or SMS 31393
- Mental Health Helpline: 0800 12 13 14 (24 hours)
- Lifeline: 0861 322 322 (24 hours)
- SADAG: 0800 456 789',
        'protocol',
        '00000000-0000-0000-0000-000000000002',
        NULL,
        ARRAY['Mental Health', 'Depression'],
        'za',
        ARRAY['mental_health', 'depression', 'suicide'],
        '{"category": "mental_health", "prescriber_level": "nurse_initiated"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0014-0000-0000-0000-000000000014',
        'Malaria Prevention and Treatment',
        'Malaria is a serious mosquito-borne disease. Prevention and early treatment are crucial.

Symptoms (typically 10-15 days after mosquito bite):
- High fever and chills
- Severe headache
- Sweating, muscle aches
- Nausea and vomiting

Prevention:
- Sleep under insecticide-treated bed nets
- Use mosquito repellent on exposed skin
- Wear long sleeves and pants at dawn and dusk
- Eliminate standing water around home
- Take antimalarial medication if prescribed for your area

When to seek immediate care:
- Any fever in malaria-endemic area
- Confusion or altered consciousness
- Difficulty breathing, seizures
- Dark or bloody urine

Malaria is curable with prompt treatment. Never self-medicate.',
        'protocol',
        '00000000-0000-0000-0000-000000000001',
        NULL,
        ARRAY['Infectious Disease', 'Malaria'],
        NULL,
        ARRAY['malaria'],
        '{"category": "infectious_disease"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0015-0000-0000-0000-000000000015',
        'Malaria Management (South Africa)',
        'Malaria-endemic areas in South Africa: Limpopo, Mpumalanga, northern KwaZulu-Natal.

Case definition:
- Fever + travel to endemic area in past 4 weeks = Malaria until proven otherwise

Diagnosis:
- Rapid Diagnostic Test (RDT) at PHC level
- Blood smear for parasite count if RDT positive
- Repeat RDT after 24 hours if negative but high suspicion

Treatment (uncomplicated P. falciparum):
- Artemether-lumefantrine (Coartem) for 3 days
- Day 0: 4 tablets at 0h and 8h
- Day 1-2: 4 tablets at 24h, 36h, 48h, 60h
- Take with fatty food for absorption

Refer urgently if:
- Cerebral malaria (confusion, seizures, coma)
- Severe anemia (Hb <7)
- Respiratory distress
- Shock
- Parasitemia >2%

All malaria cases must be notified to District within 24 hours.',
        'protocol',
        '00000000-0000-0000-0000-000000000002',
        NULL,
        ARRAY['Infectious Disease', 'Malaria'],
        'za',
        ARRAY['malaria'],
        '{"category": "infectious_disease", "notifiable_disease": true}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0016-0000-0000-0000-000000000016',
        'Diabetes Management and Self-Care',
        'Diabetes is a chronic condition affecting blood sugar processing. With proper management, people can live long, healthy lives.

Key self-care practices:
- Monitor blood glucose as recommended
- Take medications exactly as prescribed
- Follow a balanced meal plan with controlled carbohydrates
- Regular physical activity (at least 150 minutes per week)
- Check feet daily for cuts, sores, or changes
- Attend all scheduled healthcare appointments

Warning signs requiring immediate attention:
- Very high blood glucose (above 16.7 mmol/L or 300 mg/dL)
- Very low blood glucose (below 3.9 mmol/L or 70 mg/dL) with confusion
- Signs of diabetic ketoacidosis: excessive thirst, nausea, fruity breath
- Foot wounds that don''t heal

Hypoglycemia treatment:
- Symptoms: shakiness, sweating, confusion
- Treat with 15g fast-acting carbohydrate
- Recheck glucose after 15 minutes',
        'guideline',
        '00000000-0000-0000-0000-000000000001',
        NULL,
        ARRAY['Chronic Conditions', 'Diabetes'],
        NULL,
        ARRAY['diabetes'],
        '{"category": "chronic_disease"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0017-0000-0000-0000-000000000017',
        'Hypertension Management',
        'Hypertension (high blood pressure) often has no symptoms but can lead to serious complications if untreated.

Blood pressure targets:
- Normal: Less than 120/80 mmHg
- Elevated: 120-129/less than 80
- High (Stage 1): 130-139/80-89
- Hypertensive crisis: Higher than 180/120 (seek immediate care)

Lifestyle modifications:
- Reduce sodium to less than 2,300 mg per day
- DASH diet (fruits, vegetables, whole grains, lean protein)
- Maintain healthy weight
- Exercise at least 150 minutes per week
- Limit alcohol, don''t smoke
- Manage stress, get adequate sleep

Medication management:
- Take medications exactly as prescribed
- Never stop without consulting provider
- Monitor blood pressure at home

Seek immediate care if BP >180/120 with severe headache, chest pain, or vision changes.',
        'guideline',
        '00000000-0000-0000-0000-000000000001',
        NULL,
        ARRAY['Chronic Conditions', 'Hypertension'],
        NULL,
        ARRAY['hypertension', 'cardiovascular'],
        '{"category": "chronic_disease"}'::jsonb,
        NOW(),
        NOW()
    ),
    (
        'doc-0018-0000-0000-0000-000000000018',
        'South Africa Emergency Helplines',
        'Emergency and crisis helplines available in South Africa:

General Emergency:
- Police/Ambulance/Fire: 10111 or 112 from mobile
- ER24: 084 124

Health Helplines:
- National AIDS Helpline: 0800 012 322 (24 hours)
- TB Helpline: 0800 012 322
- Poisons Information: 0861 555 777 (24 hours)
- National HIV & TB Health Care Worker Hotline: 0800 212 506

Mental Health:
- Suicide Crisis Line: 0800 567 567 or SMS 31393
- Mental Health Helpline: 0800 12 13 14 (24 hours)
- Lifeline: 0861 322 322 (24 hours)
- SADAG: 0800 456 789

Gender-Based Violence:
- Stop Gender Violence: 0800 150 150 (24 hours)
- Rape Crisis: 021 447 9762

Substance Abuse:
- Alcoholics Anonymous: 0861 435 722

Chronic Disease Support:
- Diabetes SA: 086 111 3913
- Heart & Stroke Foundation: 021 422 1586',
        'reference',
        '00000000-0000-0000-0000-000000000002',
        NULL,
        ARRAY['Reference', 'Helplines'],
        'za',
        NULL,
        '{"category": "reference", "page_ref": "APC 2023 p.178"}'::jsonb,
        NOW(),
        NOW()
    )
ON CONFLICT (document_id) DO NOTHING;
