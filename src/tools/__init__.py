"""tools package - exports all available tools."""

from src.tools.triage import triage_and_risk_flagging
from src.tools.commodity import commodity_orders_and_fulfillment
from src.tools.pharmacy import pharmacy_orders_and_fulfillment
from src.tools.referrals import referrals_and_scheduling


TOOLS = {
    "triage_and_risk_flagging": triage_and_risk_flagging,
    "commodity_orders_and_fulfillment": commodity_orders_and_fulfillment,
    "pharmacy_orders_and_fulfillment": pharmacy_orders_and_fulfillment,
    "referrals_and_scheduling": referrals_and_scheduling,
}
