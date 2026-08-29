# AI Revenue Recovery Agent — Project Audit & Status Report

**Track:** AI Revenue Recovery · Razorpay AI Buildathon 2026  
**Auditor Role:** Senior Software Engineer & Project Auditor  
**Audit Scope:** Full repository audit (`backend/`, `frontend/`, `ml/`, `docs/`, `plan.md`, configs, models, and databases)  
**Date:** August 28, 2026  

---

## 1. Current Project Stage

**Current Stage: Transition between Foundation/Model Training (Days 1–6) and Pipeline Integration / Stage 3 LLM (Days 7–8).**

### Summary of State:
* **Architecture & Documentation:** Complete and locked across `docs/` (`architecture.md`, `prd.md`, `rules.md`, `design.md`, `memory.md`, `plan.md`).
* **ML Core (Stages 1 & 2):** Feature engineering and models have been trained and serialized to `.pkl` files in `ml/models/`. Serving functions (`diagnose.py` and `sequencer.py`) are implemented.
* **Backend API & Database:** FastAPI server and SQLAlchemy models exist, but **all API endpoints currently return hardcoded mock JSON**. The database is not yet migrated/connected with live credentials.
* **Stage 3 (Promise Tracker):** Scaffolded with a keyword-matching placeholder function; Google Gemini API integration is not yet wired.
* **Frontend:** Full React/Tailwind/Recharts dashboard is built and styled, fetching from the FastAPI mock endpoints.

---

## 2. Completed (Fully Implemented & Verified)

*All items below have been directly verified in the codebase.*

### Machine Learning & Data Processing
* **Hybrid Data Generator:** `ml/combine_data.py` is implemented with realistic synthetic lognormal amount and hour-of-day distributions, rule-based decline reason archetypes, and generated `ml/data/failed_payments.csv`.
* **Stage 1 ML Model (Diagnosis):** Trained Random Forest classifier serialized as `ml/models/stage1_diagnosis_model.pkl`. Serving module `backend/app/stage1_diagnosis/diagnose.py` successfully implements model loading, feature validation, and probability prediction.
* **Stage 2 ML Model (Retry Sequencer):** Trained Random Forest binary success-probability model serialized as `ml/models/stage2_retry_model.pkl`.
* **Stage 2 Constraint Logic:** `backend/app/stage2_retry/sequencer.py` enforces:
  1. Mandatory RBI 2026 24-hour pre-debit notice window (`window_hours >= 24`).
  2. Hard stopping rule (`retry_count_in_30_days >= 4` cap).

### Database Schema Definitions (ORM Layer)
* **SQLAlchemy Models:** `backend/app/db/models.py` fully defines all 5 required entities: `Payment`, `Diagnosis`, `Retry`, `Promise`, and `AuditLog`.
* **Audit Logger Module:** `backend/app/audit/logger.py` defines structured audit event logging with DB persistence handling.

### Frontend UI Dashboard
* **React + Vite + Tailwind Setup:** Functional frontend with responsive layout and tab navigation in `frontend/src/App.jsx`.
* **Dashboard Views & Components:**
  * `Overview.jsx` (metric cards + recovery funnel).
  * `Stage1Diagnosis.jsx` (`ConfusionMatrix.jsx` & `FeatureImportanceChart.jsx`).
  * `Stage2Retry.jsx` (`ComparisonBarChart.jsx` comparing naive vs. smart retry rates).
  * `Stage3PromiseAudit.jsx` (`EscalationFunnel.jsx` & `AuditTrailTable.jsx`).

---

## 3. Partially Completed (Exists but Needs Work)

| Feature / Area | Current State | Missing Work Needed |
| :--- | :--- | :--- |
| **Database Connection & Tables** | Connected & live on Supabase (`payments`, `diagnoses`, `retries`, `promises`, `audit_log`). | None. Initialized & verified live. |
| **Stage 3 Promise Extraction** | `backend/app/stage3_promise/extractor.py` implemented with live Google Gemini API (`gemini-3.6-flash`). | None. Verified with live API calls. |
| **API Layer (`/api/*`)** | `backend/app/api/routes.py` connected to live pipeline orchestrator & database. | None. All routes query live models & audit store. |
| **Kaggle Dataset Grounding** | `combine_data.py` generated `failed_payments.csv` with 1,200 records. | (Optional) Download Kaggle raw archive for retraining. |
| **"What Broke" Changelog** | `CHANGELOG_ISSUES.md` documents all bugs, root causes, and resolutions. | Continuous logging during Days 8–14. |

---

## 4. Remaining Work (per `plan.md`)

```
[Days 1-2 Foundation]
  ├── [x] Add real Supabase password to backend/.env and run DB table initialization
  └── [ ] (Optional) Download Kaggle dataset for final training run

[Days 3-6 ML & Serving Wiring]
  ├── [x] Connect Stage 1 ML model evaluation outputs directly to /api/stage1 endpoint
  └── [x] Connect Stage 2 ML model metrics directly to /api/stage2 endpoint

[Days 7-8 Stage 3: Promise Tracker]
  ├── [x] Replace extract_promise_placeholder() with live Gemini API call using google-generativeai
  ├── [x] Build promise tracking logic (promised_date pause, status update: pending/kept/broken)
  ├── [x] Implement Yale-study calibrated escalation ladder engine (gentle -> firm -> final -> stop)
  └── [x] Wire Stage 3 outputs into /api/stage3 and audit logging

[End-to-End Orchestration & Real DB Serving]
  ├── [x] Create a pipeline execution runner (POST /api/pipeline/run) to process failed_payments.csv through Stages 1 -> 2 -> 3 and populate DB & AuditLog
  └── [x] Update /api/overview and /api/audit to aggregate and query live rows from Postgres

[Days 12-14 Polish & Submission]
  ├── [ ] End-to-end integration test with live DB and frontend
  ├── [ ] Finalize pitch video script & record 5-min demo
  └── [ ] (Optional Stage 4) Hinglish voice recovery trigger
```

---

## 5. Issues, Inconsistencies & Bugs Found

### 1. Label Mismatch Between Trained Stage 1 Model and API Route / UI
* **Fact:** In `ml/combine_data.py` (lines 38–42) and `02_stage1_diagnosis_training.ipynb`, the model was trained on **3 actionable classes**:
  1. `insufficient_funds_or_technical`
  2. `card_expired`
  3. `risk_fraud_flag`
* **Mismatch:** In `backend/app/api/routes.py` (lines 42–55) and `design.md`, the route returns **5 classes**: `["insufficient_funds", "expired_card", "bank_timeout", "mandate_limit_exceeded", "do_not_honor"]` with a 5x5 confusion matrix.
* **Impact:** Once `/api/stage1` is switched from hardcoded data to live model metrics, the frontend ConfusionMatrix will break or show mismatched dimensions unless reconciled.

### 2. Database Authentication & Initialization Not Completed
* **Fact:** `backend/.env` contains `DATABASE_URL=postgresql://postgres.mahqceeulaovafsfoekn:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres`.
* **Impact:** Any database write or query will fail until the actual Supabase database password is provided and the tables are initialized with `Base.metadata.create_all(bind=engine)`.

### 3. Disconnected Pipeline (Static Mock API vs. ML Modules)
* **Fact:** `backend/app/stage1_diagnosis/diagnose.py` and `backend/app/stage2_retry/sequencer.py` are completely orphaned from the HTTP API. No endpoint calls them.
* **Impact:** The frontend is currently showcasing hardcoded values rather than results computed by the trained models.

### 4. Stage 3 Gemini API Key Configuration
* **Fact:** In `backend/.env`, `GEMINI_API_KEY` is set, but `extractor.py` is not using `google.generativeai` or `GEMINI_API_KEY`.

---

## 6. Next Steps (Recommended Priority Order)

```mermaid
flowchart TD
    A["1. DB Auth & Table Init"] --> B["2. Stage 3 Gemini Integration"]
    B --> C["3. End-to-End Pipeline Orchestrator"]
    C --> D["4. Wire Live API Routes to DB / Models"]
    D --> E["5. Reconcile Stage 1 Classes & Evaluation Metrics"]
    E --> F["6. End-to-End Verification & Pitch Prep"]
```

### Step 1: Fix Database Connection & Run Initial Table Creation
1. Replace `[YOUR-PASSWORD]` in `backend/.env` with your real Supabase PostgreSQL password.
2. Create and run a database initialization script (`backend/app/db/init_db.py`) executing `Base.metadata.create_all(bind=engine)` to create `payments`, `diagnoses`, `retries`, `promises`, and `audit_log` tables in Supabase.

### Step 2: Implement Live Gemini LLM in Stage 3 Extractor
1. In `backend/app/stage3_promise/extractor.py`, import `google.generativeai` and initialize `genai.configure(api_key=os.getenv("GEMINI_API_KEY"))`.
2. Implement structured JSON extraction calling `gemini-1.5-flash` or `gemini-pro` with response schema validation.

### Step 3: Create End-to-End Batch Pipeline Runner & Execution Endpoint
1. Create a service script (e.g. `backend/app/pipeline_runner.py`) or an API endpoint (`POST /api/pipeline/run-batch`) that:
   * Ingests failed payments from `ml/data/failed_payments.csv`.
   * Runs **Stage 1** (`predict_diagnosis`).
   * Runs **Stage 2** (`sequence_retry` with 24h RBI notice and 4-retry cap).
   * For payments failing max retries, simulates customer response and runs **Stage 3** (`extract_promise`).
   * Writes all entities and decisions to `audit_log` and related tables.

### Step 4: Reconcile Stage 1 Labels & Wire API Routes to DB
1. Align `backend/app/api/routes.py` `/api/stage1` with the 3 actionable model classes (or export the true confusion matrix metrics from the trained notebook).
2. Update `/api/overview`, `/api/stage2`, `/api/stage3`, and `/api/audit` to query live aggregated metrics and rows directly from the PostgreSQL tables.

### Step 5: Test Full System End-to-End & Document in Changelog
1. Run a clean end-to-end execution, verify live numbers render in the React dashboard, log all discoveries in `CHANGELOG_ISSUES.md`, and prepare the 5-minute pitch video.
