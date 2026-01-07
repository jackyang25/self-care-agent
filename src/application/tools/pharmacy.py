"""pharmacy orders and fulfillment tool."""

from datetime import datetime, timedelta
from typing import Optional

from langchain_core.tools import tool

from src.shared.schemas.tools import PharmacyInput, PharmacyOutput


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

    # mock data - production would integrate with pharmacy management systems
    prescription_id = "RX-67890"
    pharmacy_name = pharmacy or "Main Pharmacy"
    ready_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    return PharmacyOutput(
        message=f"prescription order placed at {pharmacy_name}",
        prescription_id=prescription_id,
        pharmacy=pharmacy_name,
        ready_date=ready_date,
        medication=medication,
        dosage=dosage,
        patient_id=patient_id,
    )
