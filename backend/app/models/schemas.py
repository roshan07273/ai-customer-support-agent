from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentDecision(str, Enum):
    approved = "approved"
    denied = "denied"
    escalated = "escalated"


class ChatRequest(BaseModel):
    customer_id: str = Field(..., examples=["CUST-1001"])
    order_id: str = Field(..., examples=["ORD-9001"])
    message: str = Field(..., min_length=3)
    channel: Literal["chat", "voice"] = "chat"


class ChatMessage(BaseModel):
    role: Literal["customer", "agent", "system"]
    content: str
    timestamp: datetime


class ToolTrace(BaseModel):
    name: str
    status: Literal["success", "warning", "failure"]
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime
    completed_at: datetime


class AgentResponse(BaseModel):
    case_id: str
    decision: AgentDecision
    customer_id: str
    order_id: str
    answer: str
    confidence: float
    tool_traces: list[ToolTrace]
    policy_citations: list[str]
    created_at: datetime


class Order(BaseModel):
    order_id: str
    item: str
    category: str
    amount: float
    currency: str
    purchase_date: date
    delivery_date: date
    status: str
    payment_status: str
    refund_status: str
    warranty_days: int
    flags: list[str] = Field(default_factory=list)


class RefundHistoryItem(BaseModel):
    order_id: str
    date: date
    amount: float
    reason: str


class CustomerProfile(BaseModel):
    customer_id: str
    name: str
    email: str
    tier: str
    risk_score: int
    orders: list[Order]
    refund_history: list[RefundHistoryItem] = Field(default_factory=list)
