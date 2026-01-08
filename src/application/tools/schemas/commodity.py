"""commodity tool schemas."""

from typing import Optional

from pydantic import BaseModel, Field

from .base import ToolResponse


class CommodityInput(BaseModel):
    """input schema for commodity orders."""

    items: str = Field(description="list of items to order (required)")
    quantity: Optional[str] = Field(None, description="quantities for each item")
    patient_id: Optional[str] = Field(None, description="patient identifier")
    priority: Optional[str] = Field(None, description="order priority: normal, urgent")


class CommodityOutput(ToolResponse):
    """output model for commodity tool."""

    message: str = Field(..., description="human-readable result message")
    order_id: Optional[str] = Field(None, description="commodity order identifier")
    estimated_delivery: Optional[str] = Field(None, description="estimated delivery date")
    items: Optional[str] = Field(None, description="ordered items")
    quantity: Optional[str] = Field(None, description="item quantities")
    patient_id: Optional[str] = Field(None, description="patient identifier")
    priority: Optional[str] = Field(None, description="order priority")

