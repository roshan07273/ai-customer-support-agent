from __future__ import annotations

from datetime import date, datetime
from typing import Any, Callable

from langchain_core.tools import tool
from pydantic import BaseModel

from app.data_store import get_customer, get_order, load_policy
from app.models.schemas import CustomerProfile, Order, ToolTrace

TODAY = date(2026, 6, 24)


def _jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, date):
        return value.isoformat()
    return value


def _trace(name: str, status: str, inputs: dict[str, Any], output: dict[str, Any], started_at: datetime) -> ToolTrace:
    return ToolTrace(
        name=name,
        status=status,
        input=_jsonable(inputs),
        output=_jsonable(output),
        started_at=started_at,
        completed_at=datetime.utcnow(),
    )


def traced_tool_call(name: str, fn: Callable[..., dict[str, Any]], **kwargs: Any) -> tuple[dict[str, Any], ToolTrace]:
    started_at = datetime.utcnow()
    try:
        output = fn(**kwargs)
        status = output.get("status", "success")
    except Exception as exc:  # Defensive trace for the admin panel and video demo.
        output = {"status": "failure", "error": str(exc)}
        status = "failure"
    return output, _trace(name, status, kwargs, output, started_at)


def find_customer_record(customer_id: str) -> dict[str, Any]:
    customer = get_customer(customer_id)
    if not customer:
        return {"status": "failure", "found": False, "message": "Customer profile was not found."}
    return {
        "status": "success",
        "found": True,
        "customer": customer.model_dump(mode="json"),
        "message": f"Loaded CRM profile for {customer.name}.",
    }


def find_order_record(customer_id: str, order_id: str) -> dict[str, Any]:
    customer = get_customer(customer_id)
    if not customer:
        return {"status": "failure", "found": False, "message": "Customer profile was not found."}
    order = get_order(customer, order_id)
    if not order:
        return {"status": "failure", "found": False, "message": "Order was not found on this customer profile."}
    return {
        "status": "success",
        "found": True,
        "order": order.model_dump(mode="json"),
        "message": f"Loaded order {order_id}.",
    }


def retrieve_refund_policy() -> dict[str, Any]:
    return {"status": "success", "policy": load_policy(), "message": "Refund policy loaded."}


def validate_refund_rules(customer: CustomerProfile, order: Order, reason: str) -> dict[str, Any]:
    citations: list[str] = []
    blockers: list[str] = []
    escalations: list[str] = []
    notes: list[str] = []

    days_since_delivery = (TODAY - order.delivery_date).days
    recent_refunds = [item for item in customer.refund_history if (TODAY - item.date).days <= 180]

    if not reason.strip():
        blockers.append("The customer did not provide a clear refund reason.")
        citations.append("Standard Eligibility #5")
    if order.status not in {"delivered", "fulfilled"}:
        blockers.append("Refunds can only be processed after delivery or fulfillment.")
        citations.append("Standard Eligibility #2")
    if order.payment_status != "paid":
        blockers.append(f"The payment status is `{order.payment_status}`, so the agent cannot refund it.")
        citations.append("Standard Eligibility #3")
    if order.refund_status != "none":
        blockers.append("This order already has a refund state on file.")
        citations.append("Standard Eligibility #4")
    if days_since_delivery > 30:
        blockers.append(f"The order is {days_since_delivery} days past delivery, outside the 30-day window.")
        citations.append("Standard Eligibility #1")

    if "final_sale" in order.flags:
        blockers.append("The item is marked final sale.")
        citations.append("Non-Refundable Rules #1")
    if "opened_hygiene_item" in order.flags and not any(word in reason.lower() for word in ["defective", "damaged"]):
        blockers.append("Opened hygiene/personal care items are not refundable unless defective or damaged.")
        citations.append("Non-Refundable Rules #2")
    if order.category == "digital" and "digital_access_used" in order.flags:
        blockers.append("Digital access has already been used.")
        citations.append("Non-Refundable Rules #3")
    if "serial_number_missing" in order.flags:
        escalations.append("The product is missing a required serial number.")
        citations.append("Non-Refundable Rules #4")
    if order.payment_status == "chargeback_open":
        blockers.append("There is an open chargeback for this order.")
        citations.append("Non-Refundable Rules #5")

    if order.amount > 300:
        escalations.append("Refund amount is above the $300 auto-approval threshold.")
        citations.append("Risk And Escalation #1")
    if customer.risk_score >= 60:
        escalations.append("Customer risk score requires human review.")
        citations.append("Risk And Escalation #2")
    if len(recent_refunds) >= 3:
        escalations.append("Customer has 3 or more refunds in the last 180 days.")
        citations.append("Risk And Escalation #3")
    if "hazmat_return_required" in order.flags:
        escalations.append("Hazmat return workflow must be confirmed before approval.")
        citations.append("Risk And Escalation #4")
    if "oversized_item" in order.flags:
        notes.append("Tell the customer pickup coordination is required for this oversized item.")
        citations.append("Risk And Escalation #5")

    if blockers:
        decision = "denied"
        status = "warning"
    elif escalations:
        decision = "escalated"
        status = "warning"
    else:
        decision = "approved"
        status = "success"

    return {
        "status": status,
        "decision": decision,
        "days_since_delivery": days_since_delivery,
        "blockers": blockers,
        "escalations": escalations,
        "notes": notes,
        "policy_citations": sorted(set(citations)),
    }


@tool
def crm_lookup_tool(customer_id: str) -> str:
    """Look up a customer profile in the CRM."""
    return str(find_customer_record(customer_id))


@tool
def order_lookup_tool(customer_id: str, order_id: str) -> str:
    """Look up an order for a customer."""
    return str(find_order_record(customer_id, order_id))


@tool
def refund_policy_tool() -> str:
    """Retrieve the current refund policy document."""
    return load_policy()
