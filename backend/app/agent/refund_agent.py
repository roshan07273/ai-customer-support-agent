from __future__ import annotations

import uuid
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.agent.tools import (
    find_customer_record,
    find_order_record,
    retrieve_refund_policy,
    traced_tool_call,
    validate_refund_rules,
)
from app.models.schemas import AgentDecision, AgentResponse, ChatRequest, CustomerProfile, Order, ToolTrace


class RefundAgent:
    def __init__(self) -> None:
        self._prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a concise e-commerce refund support agent. Use the supplied policy decision exactly. "
                    "Never override a denial or escalation. Sound helpful, natural, and firm.",
                ),
                (
                    "human",
                    "Customer: {customer_name}\nItem: {item}\nDecision: {decision}\n"
                    "Blockers: {blockers}\nEscalations: {escalations}\nNotes: {notes}\n"
                    "Customer message: {message}\nWrite the final customer-facing response.",
                ),
            ]
        )

    def run(self, request: ChatRequest) -> AgentResponse:
        traces: list[ToolTrace] = []

        customer_lookup, trace = traced_tool_call("crm_lookup", find_customer_record, customer_id=request.customer_id)
        traces.append(trace)
        if not customer_lookup.get("found"):
            return self._failure_response(request, traces, "I could not find that customer profile. Please check the customer ID and try again.")

        order_lookup, trace = traced_tool_call(
            "order_lookup",
            find_order_record,
            customer_id=request.customer_id,
            order_id=request.order_id,
        )
        traces.append(trace)
        if not order_lookup.get("found"):
            return self._failure_response(request, traces, "I found the customer, but this order is not attached to their profile.")

        _, trace = traced_tool_call("policy_retrieval", retrieve_refund_policy)
        traces.append(trace)

        customer = CustomerProfile.model_validate(customer_lookup["customer"])
        order = Order.model_validate(order_lookup["order"])
        validation, trace = traced_tool_call(
            "policy_validation",
            validate_refund_rules,
            customer=customer,
            order=order,
            reason=request.message,
        )
        traces.append(trace)

        answer = self._compose_answer(customer, order, request.message, validation)
        return AgentResponse(
            case_id=f"CASE-{uuid.uuid4().hex[:8].upper()}",
            decision=AgentDecision(validation["decision"]),
            customer_id=request.customer_id,
            order_id=request.order_id,
            answer=answer,
            confidence=0.94 if validation["decision"] == "approved" else 0.89,
            tool_traces=traces,
            policy_citations=validation["policy_citations"],
            created_at=datetime.utcnow(),
        )

    def _compose_answer(self, customer: CustomerProfile, order: Order, message: str, validation: dict) -> str:
        fallback = self._template_answer(customer, order, validation)
        try:
            model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
            chain = self._prompt | model
            result = chain.invoke(
                {
                    "customer_name": customer.name,
                    "item": order.item,
                    "decision": validation["decision"],
                    "blockers": "; ".join(validation["blockers"]) or "none",
                    "escalations": "; ".join(validation["escalations"]) or "none",
                    "notes": "; ".join(validation["notes"]) or "none",
                    "message": message,
                }
            )
            return str(result.content).strip()
        except Exception:
            return fallback

    def _template_answer(self, customer: CustomerProfile, order: Order, validation: dict) -> str:
        first_name = customer.name.split(" ")[0]
        if validation["decision"] == "approved":
            note = f" {validation['notes'][0]}" if validation["notes"] else ""
            return (
                f"Hi {first_name}, I checked your {order.item} order against our refund policy and I can approve this refund. "
                f"The refund amount is {order.currency} {order.amount:.2f}, and it will return to the original payment method once processed.{note}"
            )
        if validation["decision"] == "escalated":
            reasons = " ".join(validation["escalations"])
            return (
                f"Hi {first_name}, I reviewed your {order.item} order. I cannot auto-approve it because {reasons} "
                "I am escalating this to a human specialist so we can review the details and follow the correct return workflow."
            )
        reasons = " ".join(validation["blockers"])
        return (
            f"Hi {first_name}, I reviewed your {order.item} order and I cannot process a refund for it under the current policy. "
            f"{reasons} I can still help route you to warranty or exchange support if that fits the issue."
        )

    def _failure_response(self, request: ChatRequest, traces: list[ToolTrace], answer: str) -> AgentResponse:
        return AgentResponse(
            case_id=f"CASE-{uuid.uuid4().hex[:8].upper()}",
            decision=AgentDecision.denied,
            customer_id=request.customer_id,
            order_id=request.order_id,
            answer=answer,
            confidence=0.99,
            tool_traces=traces,
            policy_citations=[],
            created_at=datetime.utcnow(),
        )
