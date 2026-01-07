"""commodity orders and fulfillment service."""

from datetime import datetime, timedelta
from typing import Optional

from src.application.services.schemas.commodity import CommodityServiceOutput


def place_commodity_order(
    items: Optional[str] = None,
    quantity: Optional[str] = None,
    patient_id: Optional[str] = None,
    priority: Optional[str] = None,
) -> CommodityServiceOutput:
    """place a commodity order.
    
    handles ordering, pickup, or home delivery through retail and pharmacy
    partners and provides available fulfillment options.
    
    args:
        items: items to order
        quantity: quantity of items
        patient_id: patient identifier
        priority: order priority level
        
    returns:
        commodity order data
        
    raises:
        ValueError: if required fields are missing or invalid
    """
    # validate required fields
    if not items:
        raise ValueError("items are required to place an order")
    
    # validate priority
    priority_level = priority or "normal"
    if priority_level not in ["normal", "urgent"]:
        raise ValueError(f"invalid priority: {priority_level}. must be 'normal' or 'urgent'")
    
    # mock data - production would integrate with logistics/pharmacy APIs
    order_id = "ORD-12345"
    estimated_delivery = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    return CommodityServiceOutput(
        order_id=order_id,
        estimated_delivery=estimated_delivery,
        items=items,
        quantity=quantity,
        patient_id=patient_id,
        priority=priority_level,
    )

