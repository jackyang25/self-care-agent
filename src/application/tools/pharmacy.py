"""pharmacy orders and fulfillment tool."""

from typing import Optional

from langchain_core.tools import tool

from src.application.services.pharmacy import place_pharmacy_order
from src.application.tools.schemas.pharmacy import PharmacyInput, PharmacyOutput


@tool(args_schema=PharmacyInput)
def pharmacy_tool(
    medication: Optional[str] = None,
    dosage: Optional[str] = None,
    patient_id: Optional[str] = None,
    pharmacy: Optional[str] = None,
) -> PharmacyOutput:
    """manage pharmacy-specific orders, including prescription refills and over-the-counter medications that require pharmacy fulfillment.

use this tool when a user wants to refill a prescription, request pharmacy-dispensed commodities, check pharmacy inventory, or arrange pharmacy pickup or delivery. this tool is designed for items that require pharmacy workflows rather than general retail logistics.

use when: user requests a prescription refill or pharmacy-managed medication; user asks about pharmacy availability, stock, or order status; user needs support with pharmacy pickup or home delivery.

do not use for: ordering general self-test kits or non-pharmacy commodities; triage, symptom assessment, or risk evaluation; scheduling referrals, labs, or teleconsultations."""

    try:
        # call service layer
        result = place_pharmacy_order(
            medication=medication,
            dosage=dosage,
            patient_id=patient_id,
            pharmacy=pharmacy,
        )
        
        # transform service output to tool output (add presentation layer)
        return PharmacyOutput(
            status="success",
            message=f"prescription order placed at {result.pharmacy}",
            prescription_id=result.prescription_id,
            pharmacy=result.pharmacy,
            ready_date=result.ready_date,
            medication=result.medication,
            dosage=result.dosage,
            patient_id=result.patient_id,
        )
    
    except ValueError as e:
        return PharmacyOutput(
            status="error",
            message=str(e),
        )
    
    except Exception as e:
        return PharmacyOutput(
            status="error",
            message=f"pharmacy order failed: {str(e)}",
        )
