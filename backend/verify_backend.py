import os
import sys
import json
import hmac
import hashlib
from pathlib import Path
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

client = TestClient(app)

print("--- Testing /health ---")
r = client.get("/health")
print("Health status code:", r.status_code, r.json())
assert r.status_code == 200
assert r.json()["status"] == "healthy"

print("\n--- Testing /api/overview ---")
r = client.get("/api/overview")
print("Overview status code:", r.status_code)
print("Overview JSON:", r.json())
assert r.status_code == 200
data = r.json()
assert "total_payments" in data
assert "total_recovered" in data
assert "recovery_rate" in data
assert "diagnosis_accuracy" in data
assert "funnel" in data
assert "money_saved_avoiding_retries" in data
assert "risk_fraud_avoided_count" in data
print(f"Money Saved by Avoiding Bad Retries: ₹{data['money_saved_avoiding_retries']} across {data['risk_fraud_avoided_count']} fraud stops")

print("\n--- Testing /api/stage1 ---")
r = client.get("/api/stage1")
print("Stage 1 status code:", r.status_code)
print("Stage 1 labels:", r.json().get("labels"))
print("Stage 1 confusion matrix:\n", r.json().get("confusion_matrix"))
print("Stage 1 feature importance:", r.json().get("feature_importance"))
assert r.status_code == 200
assert len(r.json()["labels"]) == len(r.json()["confusion_matrix"])
assert "accuracy" in r.json()

print("\n--- Testing /api/stage2 ---")
r = client.get("/api/stage2")
print("Stage 2 status code:", r.status_code)
print("Stage 2 JSON:", r.json())
assert r.status_code == 200
assert "smart_recovery_rate" in r.json()
assert r.json().get("stopping_rule_violations") == 0
assert r.json().get("rbi_notice_violations") == 0
assert "recovery_lift_pct" in r.json()

print("\n--- Testing /api/stage3 ---")
r = client.get("/api/stage3")
print("Stage 3 status code:", r.status_code)
print("Stage 3 JSON:", r.json())
assert r.status_code == 200
assert "promises_kept" in r.json()
assert "escalation_funnel" in r.json()

print("\n--- Testing /api/audit ---")
r = client.get("/api/audit?limit=5")
print("Audit status code:", r.status_code)
print(f"Audit total count: {r.json().get('total_count')}, returned rows: {len(r.json().get('rows', []))}")
assert r.status_code == 200
assert len(r.json()["rows"]) > 0

print("\n--- Testing POST /api/pipeline/run ---")
r = client.post("/api/pipeline/run?limit=25")
print("Pipeline run status code:", r.status_code, r.json().get("message"))
assert r.status_code == 200
assert r.json()["status"] == "success"

print("\n--- Testing POST /api/stage3/extract-promise (Live Gemini test) ---")
r = client.post("/api/stage3/extract-promise", json={"customer_reply": "I will transfer INR 3500 on 2026-09-05"})
print("Live extract promise:", r.status_code, r.json())
assert r.status_code == 200
assert "is_promise" in r.json()
assert "confidence" in r.json()

print("\n--- Testing POST /api/webhook/razorpay (Security & Ingestion) ---")
test_secret = "test_webhook_secret_key_123"
os.environ["RAZORPAY_WEBHOOK_SECRET"] = test_secret

sample_payload = {
    "entity": "event",
    "event": "subscription.pending",
    "contains": ["subscription", "payment"],
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_test_live_rzp_99",
                "amount": 250000,
                "currency": "INR",
                "status": "failed",
                "error_code": "BAD_REQUEST_ERROR",
                "error_description": "Card expired on network",
                "error_reason": "card_expired"
            }
        },
        "subscription": {
            "entity": {
                "id": "sub_test_live_rzp_99",
                "status": "pending",
                "current_amount": 250000
            }
        }
    }
}
raw_bytes = json.dumps(sample_payload).encode("utf-8")
valid_sig = hmac.new(test_secret.encode("utf-8"), raw_bytes, hashlib.sha256).hexdigest()

# 1. Test missing / invalid signature
r_invalid = client.post(
    "/api/webhook/razorpay",
    content=raw_bytes,
    headers={"Content-Type": "application/json", "X-Razorpay-Signature": "invalid_signature_hex"}
)
print("Invalid signature response:", r_invalid.status_code, r_invalid.json())
assert r_invalid.status_code == 400

# 2. Test valid signature & pipeline execution
r_valid = client.post(
    "/api/webhook/razorpay",
    content=raw_bytes,
    headers={"Content-Type": "application/json", "X-Razorpay-Signature": valid_sig}
)
print("Valid signature response status:", r_valid.status_code)
assert r_valid.status_code == 200
assert r_valid.json()["status"] == "success"
assert r_valid.json()["result"]["payment_id"] == "pay_test_live_rzp_99"
assert r_valid.json()["result"]["amount_inr"] == 2500.0

print("\n--- Testing POST /api/stage4/voice-response (Keypress 1: Haan) ---")
r_voice1 = client.post("/api/stage4/voice-response", json={"payment_id": "pay_test_voice_1", "keypress": 1})
print("Voice keypress 1 response:", r_voice1.status_code, r_voice1.json())
assert r_voice1.status_code == 200
assert r_voice1.json()["action_taken"] == "promise_recorded_reminders_paused"

print("\n--- Testing POST /api/stage4/voice-response (Keypress 2: Nahi) ---")
r_voice2 = client.post("/api/stage4/voice-response", json={"payment_id": "pay_test_voice_2", "keypress": 2})
print("Voice keypress 2 response:", r_voice2.status_code, r_voice2.json())
assert r_voice2.status_code == 200
assert r_voice2.json()["action_taken"] == "escalated_outreach"

print("\n==========================================")
print("ALL BACKEND SUITE TESTS PASSED WITH 100% SUCCESS!")
print("==========================================")
