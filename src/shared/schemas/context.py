"""pydantic schema for request context.

context passed from frontend with each request, never persisted.
optimized for LMIC (low and middle-income countries) use cases.
"""

from typing import Optional
from pydantic import BaseModel, Field


class RequestContext(BaseModel):
    """context from frontend for single stateless request.

    includes both socio-technical context (LMIC-focused) and International Patient Summary (IPS):

    socio-technical context (LMIC adaptation):
    - identity: whatsapp_id for communication channel
    - patient_id: unique IPS identifier (FHIR-compliant)
    - socio-tech: literacy_level for response formatting
    - linguistics: primary_language for dialect/language
    - connectivity: network_type for media optimization
    - location: geospatial_tag for proximity calculations
    - determinants: social_context for care personalization

    international patient summary (IPS - ISO/EN 17269):
    - demographics: patient_age, patient_gender
    - conditions: active_diagnoses (chronic diseases)
    - medications: current_medications (drug-drug interactions)
    - safety: allergies (critical guardrails)
    - observations: latest_vitals (recent measurements)
    - behavioral: adherence_score, refill_due_date

    note: IPS is a curated, FHIR-standardized extract designed for cross-system
    sharing and AI clinical reasoning—not raw EMR database dumps.
    """

    # identity (communication channel)
    whatsapp_id: Optional[str] = Field(
        None, description="whatsapp phone number for communication identity"
    )

    # EMR integration
    patient_id: Optional[str] = Field(
        None,
        description="unique patient identifier in EMR system (e.g., FHIR Patient UUID)",
    )

    # socio-tech
    literacy_level: Optional[str] = Field(
        None,
        description="literacy level: 'proficient' (university/clinical), 'intermediate' (high school), 'basic' (primary school), 'below-basic' (narrative/concrete with emojis)",
    )

    # linguistics
    primary_language: Optional[str] = Field(
        None, description="primary language/dialect (e.g., 'en', 'sw', 'zu', 'fr')"
    )

    # connectivity
    network_type: Optional[str] = Field(
        None, description="network type: 'edge/2g', 'unstable', 'high-speed'"
    )

    # location
    geospatial_tag: Optional[str] = Field(
        None,
        description="location tag for proximity calculations (e.g., 'nairobi-kibera', 'cape-town-khayelitsha')",
    )

    # determinants
    social_context: Optional[str] = Field(
        None,
        description="social determinants: 'no-refrigeration', 'daily-wage-worker', 'single-parent', etc.",
    )

    # EMR context (clinical data)
    patient_age: Optional[int] = Field(
        None, ge=0, le=120, description="patient age in years (for dosage calculations)"
    )
    patient_gender: Optional[str] = Field(
        None,
        description="patient gender: 'male', 'female', 'other' (for gender-specific screening)",
    )
    active_diagnoses: Optional[str] = Field(
        None,
        description="chronic conditions (e.g., 'Type 2 Diabetes, HIV, Hypertension')",
    )
    current_medications: Optional[str] = Field(
        None, description="current medications for drug-drug interaction checks"
    )
    allergies: Optional[str] = Field(
        None, description="known allergies (e.g., 'Penicillin, Sulfa drugs')"
    )
    latest_vitals: Optional[str] = Field(
        None,
        description="recent vital signs (e.g., 'BP: 140/90, Weight: 75kg, Glucose: 180mg/dL')",
    )
    adherence_score: Optional[int] = Field(
        None, ge=0, le=100, description="medication adherence percentage (0-100%)"
    )
    refill_due_date: Optional[str] = Field(
        None, description="medication refill due date (ISO format or descriptive)"
    )
