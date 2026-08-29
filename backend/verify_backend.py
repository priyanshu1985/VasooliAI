import os
import sys
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

print("\n==========================================")
print("ALL BACKEND SUITE TESTS PASSED WITH 100% SUCCESS!")
print("==========================================")
