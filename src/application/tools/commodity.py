"""commodity orders and fulfillment tool."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from src.shared.logger import get_tool_logger, log_tool_call
from src.shared.schemas.tools import CommodityOutput

logger = get_tool_logger("commodity")


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
) -> Dict[str, Any]:
    """process commodity orders and fulfillment.
    
    args:
        items: list of items to order
        quantity: quantities for each item
        patient_id: patient identifier
        priority: order priority (normal or urgent)
        
    returns:
        dict with order confirmation details
    """
    log_tool_call(
        logger,
        "commodity_orders_and_fulfillment",
        items=items,
        quantity=quantity,
        patient_id=patient_id,
        priority=priority,
    )

    # mock data - production would integrate with logistics/pharmacy APIs
    order_id = "ORD-12345"
    estimated_delivery = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    # return pydantic model instance
    return CommodityOutput(
        order_id=order_id,
        estimated_delivery=estimated_delivery,
        items=items,
        quantity=quantity,
        patient_id=patient_id,
        priority=priority or "normal",
    ).model_dump()


commodity_tool = StructuredTool.from_function(
    func=commodity_orders_and_fulfillment,
    name="commodity_orders_and_fulfillment",
    description="""help users order self-tests, medicines, or other health commodities.

use this tool when a user wants to request, purchase, or refill a commodity such as a self-test kit, over-the-counter medicine, contraception, or related supplies. the tool orchestrates ordering, pickup, or home delivery through retail and pharmacy partners and can provide available fulfillment options.

use when: user wants to order or reorder a health commodity; user asks about pickup, delivery, or availability of a specific item; user wants to check or manage the status of an existing commodity order.

do not use for: prescription-only pharmacy orders; symptom assessment or medical triage; scheduling labs, teleconsults, or clinical appointments.""",
    args_schema=CommodityInput,
)
