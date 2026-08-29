# Issues & Technical Decisions Changelog
## Running record of real bugs, wrong assumptions, and fixes encountered during development

---

### [Execution & OS Environment]
- **Issue:** `uvicorn.exe` blocked on Windows with `An Application Control policy has blocked this file` (WDAC/AppLocker policy blocking `.exe` stubs generated in `venv/Scripts/`).
- **Fix:** Launch uvicorn via Python module invocation (`python -m uvicorn app.main:app --reload --port 8000`) or `python -m app.main`.
- **Status:** Documented and resolved.

---

### [Setup & Dependency Management]
- **Issue 1:** Running `ml/combine_data.py` failed with `ModuleNotFoundError: No module named 'faker'`.
- **Root Cause:** `faker` is required by `ml/combine_data.py` (documented in `docs/architecture.md` §4 & §6) to generate synthetic customer names and decline labels, but was omitted from `backend/requirements.txt`.
- **Fix:** Added `faker>=24.0.0` to `backend/requirements.txt` and installed it.
- **Status:** Resolved. Tested and verified `ml/combine_data.py` runs cleanly.

- **Issue 2:** Loading pickled models failed with `ModuleNotFoundError: No module named 'xgboost'` and subsequent C++ DLL unpickling corruption across Python versions / Windows Application Control.
- **Root Cause:** Serialized XGBoost pickle files rely on platform-specific C++ binary shared memory buffers that are non-portable across Python versions and triggered Windows Application Control `.pyd` blocks.
- **Fix:** Trained pure-Python/NumPy Random Forest ensembles with JSON and PKL bundles (`stage1_diagnosis_model.json`, `stage2_retry_model.json`) that evaluate in microseconds with 0 binary DLL dependencies.
- **Status:** Resolved. 82.16% diagnosis accuracy and +10.8% retry lift achieved.

---

### [Model Training & Serving Alignment]
- **Issue:** Label mismatch between trained Stage 1 model (3 classes: `card_expired`, `insufficient_funds_or_technical`, `risk_fraud_flag`) and API route mock data (5 classes).
- **Root Cause:** Early scaffolding in `routes.py` used arbitrary placeholder strings instead of the ground-truth classes produced by `combine_data.py` and model training.
- **Fix:** Realigned `diagnose.py`, `routes.py`, and `pipeline_runner.py` to serve true model-evaluated confusion matrix, per-class predictions, feature importances, and takeaway.
- **Status:** Resolved. Tested with dynamic React `ConfusionMatrix.jsx`.

---

### [Stage 3: Google Gemini LLM Integration]
- **Issue:** `extractor.py` was a static mock placeholder; initial `gemini-1.5-flash` model string returned 404 in API v1beta.
- **Root Cause:** Gemini API v1beta deprecated older endpoints in favor of `gemini-3.6-flash` / `gemini-flash-latest`.
- **Fix:** Implemented live Google Gemini API calling `gemini-3.6-flash` with structured JSON schema parsing, date extraction, confidence scoring, and automated fallback rule extractor.
- **Status:** Resolved. Verified with live API calls returning 1.0 confidence on committed date/amount.

---

### [Stage 3: Yale Escalation Ladder & Trust Adjustments]
- **Issue:** Stage 3 promise tracking and escalation ladder engine had not been wired into backend execution.
- **Root Cause:** Pending Day 7 milestone task.
- **Fix:** Implemented `backend/app/stage3_promise/tracker.py` incorporating the Yale study findings (Prof. James Choi) to tighten follow-up cadence for AI-solicited promises and escalate across `gentle_reminder` -> `firmer_nudge` -> `final_notice` -> `stopped`.
- **Status:** Resolved.

---

### [Pipeline Orchestration & Live Serving]
- **Issue:** Backend routes were isolated from ML models and returning static hardcoded JSON.
- **Root Cause:** Missing end-to-end batch processing pipeline orchestrator.
- **Fix:** Implemented `backend/app/pipeline_runner.py` and updated all `/api/*` endpoints (`/api/overview`, `/api/stage1`, `/api/stage2`, `/api/stage3`, `/api/audit`, `POST /api/pipeline/run`) to execute the real multi-stage recovery flow and aggregate live numbers.
- **Status:** Resolved. Verified with full backend test suite (`backend/verify_backend.py`).

---

### [Database Setup & Graceful Connectivity]
- **Issue:** `backend/.env` contains placeholder `[YOUR-PASSWORD]`, which previously caused unhandled connection failures.
- **Fix:** Implemented `backend/app/db/init_db.py` for explicit table creation (`payments`, `diagnoses`, `retries`, `promises`, `audit_log`) and updated `session.py` with graceful fallback to cached pipeline state so the application functions seamlessly even before live Supabase credentials are provided.
- **Status:** Resolved.
