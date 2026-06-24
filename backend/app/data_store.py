from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.models.schemas import CustomerProfile, Order

DATA_DIR = Path(__file__).parent / "data"
CRM_PATH = DATA_DIR / "crm_profiles.json"
POLICY_PATH = DATA_DIR / "refund_policy.md"


@lru_cache(maxsize=1)
def load_profiles() -> list[CustomerProfile]:
    raw_profiles = json.loads(CRM_PATH.read_text(encoding="utf-8"))
    return [CustomerProfile.model_validate(profile) for profile in raw_profiles]


@lru_cache(maxsize=1)
def load_policy() -> str:
    return POLICY_PATH.read_text(encoding="utf-8")


def get_customer(customer_id: str) -> CustomerProfile | None:
    return next((profile for profile in load_profiles() if profile.customer_id == customer_id), None)


def get_order(customer: CustomerProfile, order_id: str) -> Order | None:
    return next((order for order in customer.orders if order.order_id == order_id), None)
