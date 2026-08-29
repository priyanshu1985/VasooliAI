# AI Revenue Recovery Agent
> **Track:** AI Revenue Recovery — Razorpay AI Buildathon 2026

An automated multi-stage revenue recovery agent that combines classical ML classification for root cause diagnosis and retry sequencing with Google Gemini LLM for conversational promise-to-pay extraction, fully compliant with the RBI 2026 e-mandate framework.

---

## 📚 Project Documentation

All design decisions, schemas, and requirements are documented in the [`docs/`](docs/) directory:
- [**Product Requirements (PRD)**](docs/prd.md) — Problem statement, goals, scope, and target metrics.
- [**Architecture Document**](docs/architecture.md) — System design, ML vs. LLM justification, data flow, and directory structure.
- [**Non-Negotiable Rules**](docs/rules.md) — Hard constraints (e.g. stopping rules, ML integrity, Postgres requirement).
- [**14-Day Plan**](docs/plan.md) — Build roadmap and milestone checklists.
- [**Dashboard Design Spec**](docs/design.md) — UI/UX specification and backend JSON data contracts.
- [**Decision Memory Log**](docs/memory.md) — Architectural rationale and locked technical choices.

---

## 🏗️ Architecture Summary

```
Failed Recurring Payment
          │
          ▼
 [STAGE 1: Diagnose]  ── (Random Forest Classifier) ──► Failure Reason & Confidence
          │
          ▼
 [STAGE 2: Decide+Act] ── (Binary ML Sequencer) ──► Optimal Retry Window (RBI 24h & 4-Retry Compliant)
          │                                                    │
          │                                  (If retries exhausted / hard stop)
          │                                                    ▼
          │                                       [STAGE 3: Promise Tracker] ── (Gemini LLM) ──► Structured Promise
          │                                                    │
          │                                       (Yale-Study Calibrated Escalation)
          │                                                    │
          ▼                                                    ▼
                 POSTGRESQL AUDIT TRAIL (100% Traceability)
                                  │
                                  ▼
           REACT DASHBOARD (Overview, Metrics, Confusion Matrix, Funnels)
```

---

## 🚀 Local Development Setup

### 1. Backend (FastAPI)

```bash
# Navigate to backend directory
cd backend

# (Optional) Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template and configure secrets
cp .env.example .env
# Edit .env with your DATABASE_URL (Supabase/Postgres) and GEMINI_API_KEY

# Start the FastAPI server (starts on http://localhost:8000)
uvicorn app.main:app --reload --port 8000
```

- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

---

### 2. Frontend (React + Vite + Tailwind + Recharts)

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Copy environment template
cp .env.example .env

# Start the Vite development server (starts on http://localhost:5173)
npm run dev
```

- Dashboard: [http://localhost:5173](http://localhost:5173)

---

### 3. Live Razorpay Webhooks (via Cloudflare Tunnel)

To receive live payment failure and subscription degradation webhooks from the Razorpay Dashboard:

```powershell
# Expose local FastAPI backend on a Cloudflare HTTPS tunnel
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:8000
```

1. Copy your generated `https://<subdomain>.trycloudflare.com` URL from the terminal output.
2. In **Razorpay Dashboard** $\rightarrow$ **Settings** $\rightarrow$ **Webhooks**:
   - **Webhook URL:** `https://<subdomain>.trycloudflare.com/api/webhook/razorpay`
   - **Secret:** The same secret configured in `backend/.env` under `RAZORPAY_WEBHOOK_SECRET`
   - **Active Events:** `subscription.pending`, `payment.failed`, `subscription.charged`
3. Any failed recurring charge or subscription event will automatically trigger the 3-stage recovery pipeline and stream to the audit trail.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python 3.10+), SQLAlchemy 2.0, Pydantic v2
- **ML Models:** scikit-learn (Random Forest & Binary Classifiers), joblib
- **LLM Layer:** Google Gemini API (Free tier via Google AI Studio)
- **Database:** PostgreSQL (Supabase Free Tier)
- **Frontend:** React (Vite), Tailwind CSS, Recharts, Lucide Icons
