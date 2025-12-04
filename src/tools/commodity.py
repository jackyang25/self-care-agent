"""commodity orders and fulfillment tool."""

from typing import Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class CommodityInput(BaseModel):
    """input schema for commodity orders."""

    items: Optional[str] = Field(None, description="list of items to order")
    quantity: Optional[str] = Field(None, description="quantities for each item")
    patient_id: Optional[str] = Field(None, description="patient identifier")
    priority: Optional[str] = Field(None, description="order priority: normal, urgent")


def commodity_orders_and_fulfillment(
    items: Optional[str] = None,
    quantity: Optional[str] = None,
    patient_id: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """process commodity orders and fulfillment. use this for ordering medical supplies, equipment, or other commodities."""
    print(f"[TOOL CALLED] commodity_orders_and_fulfillment")
    print(
        f"[ARGUMENTS] items={items}, quantity={quantity}, patient_id={patient_id}, priority={priority}"
    )

    order_id = "ORD-12345"
    estimated_delivery = "2025-12-10"

    return f"order processed successfully. order_id: {order_id}, estimated_delivery: {estimated_delivery}. status: success"


commodity_tool = StructuredTool.from_function(
    func=commodity_orders_and_fulfillment,
    name="commodity_orders_and_fulfillment",
    description="process commodity orders and fulfillment. use for ordering medical supplies, equipment, or other commodities.",
    args_schema=CommodityInput,
)
