"""commodity orders and fulfillment tool."""

from typing import Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from src.utils.logger import get_logger

logger = get_logger("commodity")


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
    logger.info("commodity_orders_and_fulfillment called")
    logger.debug(
        f"arguments: items={items}, quantity={quantity}, patient_id={patient_id}, priority={priority}"
    )

    order_id = "ORD-12345"
    estimated_delivery = "2025-12-10"

    return f"order processed successfully. order_id: {order_id}, estimated_delivery: {estimated_delivery}. status: success"


commodity_tool = StructuredTool.from_function(
    func=commodity_orders_and_fulfillment,
    name="commodity_orders_and_fulfillment",
    description="""help users order self-tests, medicines, or other health commodities.

use this tool when a user wants to request, purchase, or refill a commodity such as a self-test kit, over-the-counter medicine, contraception, or related supplies. the tool orchestrates ordering, pickup, or home delivery through retail and pharmacy partners and can provide available fulfillment options.

use when: user wants to order or reorder a health commodity; user asks about pickup, delivery, or availability of a specific item; user wants to check or manage the status of an existing commodity order.

do not use for: prescription-only pharmacy orders; symptom assessment or medical triage; scheduling labs, teleconsults, or clinical appointments.""",
    args_schema=CommodityInput,
)
