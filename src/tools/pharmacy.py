"""pharmacy orders and fulfillment tool."""

import json
from typing import Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from src.utils.logger import get_logger

logger = get_logger("pharmacy")


class PharmacyInput(BaseModel):
    """input schema for pharmacy orders."""

    medication: Optional[str] = Field(
        None, description="medication name or prescription"
    )
    dosage: Optional[str] = Field(None, description="dosage instructions")
    patient_id: Optional[str] = Field(None, description="patient identifier")
    pharmacy: Optional[str] = Field(None, description="preferred pharmacy location")


def pharmacy_orders_and_fulfillment(
    medication: Optional[str] = None,
    dosage: Optional[str] = None,
    patient_id: Optional[str] = None,
    pharmacy: Optional[str] = None,
) -> str:
    """process pharmacy orders and prescription fulfillment. use this for ordering medications, prescriptions, or pharmacy services."""
    logger.info("pharmacy_orders_and_fulfillment called")
    logger.debug(
        f"arguments: medication={medication}, dosage={dosage}, patient_id={patient_id}, pharmacy={pharmacy}"
    )

    prescription_id = "RX-67890"
    pharmacy_name = pharmacy or "main pharmacy"
    ready_date = "2025-12-05"

    # return structured json response
    result = {
        "status": "success",
        "prescription_id": prescription_id,
        "pharmacy": pharmacy_name,
        "ready_date": ready_date,
        "medication": medication,
        "dosage": dosage,
        "patient_id": patient_id,
    }
    
    return json.dumps(result, indent=2)


pharmacy_tool = StructuredTool.from_function(
    func=pharmacy_orders_and_fulfillment,
    name="pharmacy_orders_and_fulfillment",
    description="""manage pharmacy-specific orders, including prescription refills and over-the-counter medications that require pharmacy fulfillment.

use this tool when a user wants to refill a prescription, request pharmacy-dispensed commodities, check pharmacy inventory, or arrange pharmacy pickup or delivery. this tool is designed for items that require pharmacy workflows rather than general retail logistics.

use when: user requests a prescription refill or pharmacy-managed medication; user asks about pharmacy availability, stock, or order status; user needs support with pharmacy pickup or home delivery.

do not use for: ordering general self-test kits or non-pharmacy commodities; triage, symptom assessment, or risk evaluation; scheduling referrals, labs, or teleconsultations.""",
    args_schema=PharmacyInput,
)
