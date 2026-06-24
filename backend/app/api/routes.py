from __future__ import annotations

from fastapi import APIRouter

from app.agent.refund_agent import RefundAgent
from app.data_store import load_profiles
from app.models.schemas import AgentResponse, ChatRequest, CustomerProfile

router = APIRouter()
agent = RefundAgent()
case_log: list[AgentResponse] = []


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/customers", response_model=list[CustomerProfile])
def customers() -> list[CustomerProfile]:
    return load_profiles()


@router.post("/chat", response_model=AgentResponse)
def chat(request: ChatRequest) -> AgentResponse:
    response = agent.run(request)
    case_log.insert(0, response)
    return response


@router.get("/cases", response_model=list[AgentResponse])
def cases() -> list[AgentResponse]:
    return case_log[:30]
