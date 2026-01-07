"""pharmacy orders and fulfillment service."""

from datetime import datetime, timedelta
from typing import Optional

from src.shared.schemas.services import PharmacyServiceOutput


def place_pharmacy_order(
    medication: Optional[str] = None,
    dosage: Optional[str] = None,
    patient_id: Optional[str] = None,
    pharmacy: Optional[str] = None,
) -> PharmacyServiceOutput:
    """place a pharmacy order for prescription or OTC medications.
    
    handles prescription refills, pharmacy-dispensed commodities, inventory
    checks, and arranges pharmacy pickup or delivery.
    
    args:
        medication: medication name
        dosage: medication dosage
        patient_id: patient identifier
        pharmacy: preferred pharmacy name
        
    returns:
        pharmacy order data
        
    raises:
        ValueError: if required fields are missing
    """
    # validate required fields
    if not medication:
        raise ValueError("medication is required to place a pharmacy order")
    
    # mock data - production would integrate with pharmacy management systems
    prescription_id = "RX-67890"
    pharmacy_name = pharmacy or "Main Pharmacy"
    ready_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    return PharmacyServiceOutput(
        prescription_id=prescription_id,
        pharmacy=pharmacy_name,
        ready_date=ready_date,
        medication=medication,
        dosage=dosage,
        patient_id=patient_id,
    )

