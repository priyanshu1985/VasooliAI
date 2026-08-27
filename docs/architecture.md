# Architecture Document
## AI Revenue Recovery Agent — Razorpay AI Buildathon 2026

---

## 1. High-Level Concept

This project implements the pattern Razorpay itself hinted at in the track description: **Payment degradation → root cause → recovery action.** It is built as one chained pipeline, not three disconnected demos:

```
Failed Payment
     |
     v
[STAGE 1: Diagnose]  --(ML classifier)-->  reason + confidence
     |
     v
[STAGE 2: Decide+Act] --(ML model)-->  best retry window --> execute retry (simulated)
     |                                                              |
     |                                            (still failing after max retries)
     |                                                              v
     |                                              [STAGE 3: Promise Tracker] --(LLM)--> extracted promise
     |                                                              |
     |                                              pause + auto re-check on promised date
     |                                                              |
     v                                                              v
                    AUDIT TRAIL (every decision, every stage, logged)
                                       |
                                       v
                          DASHBOARD (React) — metrics, charts, audit log

[Optional Stage 4: Hinglish Voice] -- sits alongside Stage 3, only if unresponsive over text
```

---

## 2. Why Each Stage Uses the Tool It Uses (this is your strongest architecture talking point)

This is the single most important design decision in the whole project, and it should be stated explicitly in the pitch:

- **Stage 1 and Stage 2 use trained ML models (scikit-learn / XGBoost)**, not an LLM, because both tasks are **structured prediction from numeric/categorical features** — decline codes, amounts, timestamps, retry counts. This kind of task is exactly what classical ML is good at, and critically, it is **provable**: a confusion matrix, precision/recall, and feature importance chart give a judge hard evidence of what the model actually learned.
- **Stage 3 uses an LLM (Google Gemini API, free tier)**, because it requires genuine **freeform language understanding** — reading a customer's typed reply like "will do by next week" and extracting a structured commitment. Training a classical model for this from scratch would require thousands of hand-labeled real conversations, which do not exist for this project's timeline. Real companies (Skit.ai, IRIS Insights) use conversational AI specifically for this piece of the pipeline, not the whole system — this project mirrors that same reasoning.
- **The takeaway for judges:** "We used a trained ML model everywhere the task was structured prediction, because that's measurable and defensible. We used an LLM only for the one task that genuinely requires language understanding."

---

## 3. Component Breakdown

### Stage 1 — Diagnosis Engine (ML Classifier)
- **Input features:** decline code, payment amount, retry count so far, hour of day, day of week, customer's past failure count, subscription age
- **Model:** Random Forest or XGBoost multi-class classifier
- **Output:** `{predicted_reason, confidence_score}`
- **Evaluation artifacts:** confusion matrix, per-class precision/recall, feature importance chart

### Stage 2 — Retry Sequencer (ML Model)
- **Input features:** same base features as Stage 1, plus candidate retry window (next-day morning / next-day evening / 3 days later / 7 days later), simulated customer "pay-pattern" signal
- **Model:** binary classifier predicting probability of retry success per candidate window
- **Decision rule:** pick the candidate window with the highest predicted success probability
- **Hard constraints (non-negotiable, enforced in code, not just prompted):**
  - No retry may be scheduled inside the 24-hour RBI pre-debit notice window
  - Max 4 retries within a rolling 30-day period per payment
- **Evaluation artifact:** naive fixed-schedule baseline vs. model-picked windows, run on the same test batch, compared side by side

### Stage 3 — Promise Tracker (LLM)
- **Input:** simulated customer freeform reply text
- **Model:** Google Gemini API (free tier), prompted to return strict JSON: `{promised_date, promised_amount, confidence}`
- **Logic layer (not the LLM's job — this is plain code):**
  - Pause all reminders until promised_date
  - Auto re-check on that date; mark promise kept/broken
  - Maintain a per-customer "promise reliability" score
  - Apply a stricter default follow-up cadence than a naive system would, specifically because research (Yale study, cited in research PDF) shows AI-made promises are broken more often than human-made ones
  - Escalation ladder: gentle reminder → firmer nudge → final notice → stop (hard cap, never infinite)

### Audit Trail
- Every decision from every stage is written as a row: `{timestamp, stage, payment_id, decision, reasoning_inputs, outcome}`
- This is not optional polish — it is a directly graded requirement per Razorpay's own track description

### Dashboard (React + Vite + Tailwind + Recharts)
- Pages: Overview (headline metrics), Stage 1 (confusion matrix + feature importance), Stage 2 (naive vs. smart comparison), Stage 3 (promise-kept rate + escalation funnel), Audit Trail (searchable table)
- See design.md for full page-by-page layout

---

## 4. Tech Stack Reference Table

| Layer | Choice | Notes |
|---|---|---|
| Backend/API | FastAPI (Python) | serves all stage endpoints + dashboard data as JSON |
| Stage 1 model | scikit-learn / XGBoost | multi-class classifier |
| Stage 2 model | scikit-learn / XGBoost | binary success-probability classifier |
| Stage 3 model | Google Gemini API (free tier) | structured JSON extraction from freeform text |
| Database | PostgreSQL via Supabase (free tier) | persists across redeploys, unlike SQLite |
| Frontend | React (Vite) + Tailwind CSS + Recharts | lightweight, genuinely production-style |
| Data | Real Kaggle transaction dataset (structure) + Faker-generated labels (decline reason, retry outcome) | see ml/README.md for exact combination method |
| Hosting (suggested) | Backend: Render or Railway free tier · Frontend: Vercel or Netlify free tier · DB: Supabase free tier | all no-cost, all support this stack natively |
| Version control | GitHub (public repo) | required by submission rules |

---

## 5. What You Must Set Up Externally (cannot be done inside this build environment)

1. **Kaggle account + dataset download** — create a free Kaggle account, install the `kaggle` CLI, and download the dataset named in `ml/README.md`. This cannot be fetched automatically here.
2. **Google AI Studio account** — go to https://ai.google.dev, sign in with a Google account, generate a free Gemini API key. No credit card required.
3. **Supabase account** — create a free project at https://supabase.com to get a hosted Postgres connection string.
4. **GitHub repository** — create the public repo that will hold this project for submission.
5. **Deployment accounts** (only needed if you deploy live, not just for local dev/demo):
   - Render or Railway account for the FastAPI backend
   - Vercel or Netlify account for the React frontend

---

## 6. Data Flow Summary

1. Real Kaggle CSV loaded → realistic amount/time distributions extracted
2. Faker generates synthetic subscription-failure records using those distributions, with hidden ground-truth decline reasons attached
3. Stage 1 model trained/evaluated on this combined dataset
4. Stage 2 training data derived by expanding each failed payment into multiple candidate retry-window rows with simulated outcomes
5. Stage 2 model trained/evaluated; naive baseline computed for comparison
6. Stage 3 runs live against the Gemini API for any payment that exhausts retries
7. Every stage writes to the Postgres audit trail
8. FastAPI exposes aggregated metrics + raw audit rows as JSON
9. React dashboard fetches and renders all of the above

---

## 7. Project Directory Structure

```
razorpay-revenue-recovery/
│
├── docs/                          # this planning documentation set
│   ├── prd.md
│   ├── architecture.md
│   ├── rules.md
│   ├── plan.md
│   ├── design.md
│   └── memory.md
│
├── ml/                             # everything ML: training + saved models
│   ├── notebooks/
│   │   ├── 01_data_exploration.ipynb
│   │   ├── 02_stage1_diagnosis_training.ipynb
│   │   └── 03_stage2_retry_training.ipynb
│   ├── data/
│   │   ├── kaggle_raw/             # real downloaded Kaggle CSV (gitignored)
│   │   └── failed_payments.csv     # combined hybrid dataset (gitignored)
│   ├── models/                     # saved trained models, output of the notebooks
│   │   ├── stage1_diagnosis_model.pkl
│   │   └── stage2_retry_model.pkl
│   ├── outputs/                    # confusion matrix / chart images (gitignored)
│   ├── combine_data.py             # data generation script (stays plain .py — a single linear pass, not something explored interactively)
│   └── README.md
│
├── backend/                        # FastAPI app — plain Python, serves the trained models
│   ├── app/
│   │   ├── main.py                 # FastAPI app entrypoint
│   │   ├── stage1_diagnosis/
│   │   │   └── diagnose.py         # loads stage1_diagnosis_model.pkl, exposes predict function
│   │   ├── stage2_retry/
│   │   │   └── sequencer.py        # loads stage2_retry_model.pkl, applies RBI + stopping rules
│   │   ├── stage3_promise/
│   │   │   └── extractor.py        # calls Gemini API, extracts promise JSON
│   │   ├── audit/
│   │   │   └── logger.py           # writes every decision to the audit_log table
│   │   ├── db/
│   │   │   ├── models.py           # SQLAlchemy table definitions
│   │   │   └── session.py          # Postgres/Supabase connection
│   │   └── api/
│   │       └── routes.py           # the /api/overview, /api/stage1, etc. endpoints from design.md
│   ├── requirements.txt
│   └── .env.example                # placeholder for API keys / DB URL, real .env is gitignored
│
├── frontend/                       # React (Vite) app
│   ├── src/
│   │   ├── components/             # MetricCard, ComparisonBarChart, ConfusionMatrix,
│   │   │   ...                     # FeatureImportanceChart, EscalationFunnel, AuditTrailTable, NavBar
│   │   ├── pages/                  # Overview, Stage1Diagnosis, Stage2Retry, Stage3PromiseAudit
│   │   ├── api/
│   │   │   └── client.js           # fetch wrapper for calling the FastAPI backend
│   │   └── App.jsx
│   ├── package.json
│   └── .env.example                # placeholder for backend API URL
│
├── CHANGELOG_ISSUES.md              # running "what broke" log — start from day 1, per rules.md
├── .gitignore
└── README.md                        # top-level: what this project is, how to run it, architecture summary
```

**Why notebooks for training, plain `.py` for serving:** notebooks are the right tool for the *exploration and training* phase — inspecting a dataframe mid-pipeline, rerunning just one cell after tweaking a hyperparameter, seeing a confusion matrix render immediately below the cell that made it. They are the wrong tool for anything that must run automatically inside the live backend. So training happens once, interactively, in `ml/notebooks/`; the notebook's last step saves the trained model to a `.pkl` file in `ml/models/`; and the backend's `stage1_diagnosis/diagnose.py` / `stage2_retry/sequencer.py` simply **load that saved file** rather than retraining live. This mirrors how real ML teams split "figuring out the model" from "shipping the model."

