"""pharmacy service output schema."""

from typing import Optional

from pydantic import BaseModel


class PharmacyServiceOutput(BaseModel):
    """output from pharmacy order service."""
    
    prescription_id: str
    pharmacy: str
    ready_date: str
    medication: Optional[str] = None
    dosage: Optional[str] = None
    patient_id: Optional[str] = None

