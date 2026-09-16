#!/bin/bash
# 작은 결제 모듈 픽스처. 얕은 모듈·정보 누수·pass-through가 드러나도록 만든 예제다.
set -e
mkdir -p src/payment tests
cat > src/payment/gateway.py <<'PY'
import requests

class StripeGateway:
    def charge(self, amount_cents: int, token: str) -> dict:
        r = requests.post("https://api.stripe.example/charge", json={"amount": amount_cents, "source": token})
        return r.json()  # {"id": "...", "status": "succeeded" | "failed"}
PY
cat > src/payment/service.py <<'PY'
from .gateway import StripeGateway

class PaymentService:
    def __init__(self):
        self.gateway = StripeGateway()

    def charge(self, amount_cents, token):
        return self.gateway.charge(amount_cents, token)

    def charge_order(self, order, token):
        result = self.gateway.charge(int(order["total"] * 100), token)
        if result["status"] == "succeeded":
            order["state"] = "PAID"
            order["stripe_charge_id"] = result["id"]
        return order
PY
cat > src/payment/report.py <<'PY'
def paid_orders(orders):
    return [o for o in orders if o.get("state") == "PAID" and o.get("stripe_charge_id")]
PY
cat > tests/test_service.py <<'PY'
from unittest.mock import patch
from src.payment.service import PaymentService

@patch("src.payment.gateway.requests.post")
def test_charge_order_marks_paid(post):
    post.return_value.json.return_value = {"id": "ch_1", "status": "succeeded"}
    order = PaymentService().charge_order({"total": 10.0}, "tok")
    assert order["state"] == "PAID"
PY
# 두 번째 모듈 — "대상 없음" 케이스에서 어느 모듈을 볼지 물어야만 하게 만든다.
mkdir -p src/shipping
cat > src/shipping/quote.py <<'PY'
RATES = {"KR": 3000, "US": 15000}

def quote(country: str, weight_kg: float) -> int:
    base = RATES.get(country, 20000)
    return base + int(weight_kg * 500)
PY
