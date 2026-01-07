"""commodity service output schema."""

from typing import Optional

from pydantic import BaseModel


class CommodityServiceOutput(BaseModel):
    """output from commodity order service."""
    
    order_id: str
    estimated_delivery: str
    items: Optional[str] = None
    quantity: Optional[str] = None
    patient_id: Optional[str] = None
    priority: str

