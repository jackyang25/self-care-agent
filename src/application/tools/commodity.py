"""commodity orders and fulfillment tool."""

from datetime import datetime, timedelta
from typing import Optional

from langchain_core.tools import tool

from src.shared.schemas.tools import CommodityInput, CommodityOutput


@tool(args_schema=CommodityInput)
def commodity_tool(
    items: Optional[str] = None,
    quantity: Optional[str] = None,
    patient_id: Optional[str] = None,
    priority: Optional[str] = None,
) -> CommodityOutput:
    """help users order self-tests, medicines, or other health commodities.

use this tool when a user wants to request, purchase, or refill a commodity such as a self-test kit, over-the-counter medicine, contraception, or related supplies. the tool orchestrates ordering, pickup, or home delivery through retail and pharmacy partners and can provide available fulfillment options.

use when: user wants to order or reorder a health commodity; user asks about pickup, delivery, or availability of a specific item; user wants to check or manage the status of an existing commodity order.

do not use for: prescription-only pharmacy orders; symptom assessment or medical triage; scheduling labs, teleconsults, or clinical appointments."""

    # mock data - production would integrate with logistics/pharmacy APIs
    order_id = "ORD-12345"
    estimated_delivery = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    priority_level = priority or "normal"

    return CommodityOutput(
        message=f"commodity order placed: {order_id}",
        order_id=order_id,
        estimated_delivery=estimated_delivery,
        items=items,
        quantity=quantity,
        patient_id=patient_id,
        priority=priority_level,
    )
