"""pharmacy orders and fulfillment tool."""

from typing import Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


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
    print(f"[TOOL CALLED] pharmacy_orders_and_fulfillment")
    print(
        f"[ARGUMENTS] medication={medication}, dosage={dosage}, patient_id={patient_id}, pharmacy={pharmacy}"
    )

    prescription_id = "RX-67890"
    pharmacy_name = pharmacy or "main pharmacy"
    ready_date = "2025-12-05"

    return f"prescription order processed. prescription_id: {prescription_id}, pharmacy: {pharmacy_name}, ready_date: {ready_date}. status: success"


pharmacy_tool = StructuredTool.from_function(
    func=pharmacy_orders_and_fulfillment,
    name="pharmacy_orders_and_fulfillment",
    description="process pharmacy orders and prescription fulfillment. use for ordering medications, prescriptions, or pharmacy services.",
    args_schema=PharmacyInput,
)
