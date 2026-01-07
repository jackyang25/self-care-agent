"""commodity orders and fulfillment tool."""

from typing import Optional

from langchain_core.tools import tool

from src.application.services.commodity import place_commodity_order
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

    try:
        # call service layer
        result = place_commodity_order(
            items=items,
            quantity=quantity,
            patient_id=patient_id,
            priority=priority,
        )
        
        # transform service output to tool output (add presentation layer)
        return CommodityOutput(
            status="success",
            message=f"commodity order placed: {result.order_id}",
            order_id=result.order_id,
            estimated_delivery=result.estimated_delivery,
            items=result.items,
            quantity=result.quantity,
            patient_id=result.patient_id,
            priority=result.priority,
        )
    
    except ValueError as e:
        return CommodityOutput(
            status="error",
            message=str(e),
        )
    
    except Exception as e:
        return CommodityOutput(
            status="error",
            message=f"commodity order failed: {str(e)}",
        )
