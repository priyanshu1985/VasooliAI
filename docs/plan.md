# Plan.md
## 14-Day Build Plan — AI Revenue Recovery Agent

Track: AI Revenue Recovery · Razorpay AI Buildathon 2026
Scope: Failed-Subscription Recovery → Mandate Retry Sequencer → Promise-to-Pay Tracker (+ optional Stage 4: Hinglish Voice)

---

## Days 1–2 — Foundation
- [ ] Create public GitHub repo
- [ ] Set up FastAPI project skeleton
- [ ] Set up Supabase Postgres project; get connection string; add to `.env`
- [ ] Create DB schema: `payments`, `diagnoses`, `retries`, `promises`, `audit_log`
- [ ] Download real Kaggle dataset (see ml/README.md for exact dataset + command)
- [ ] Run `ml/combine_data.py` to generate the hybrid dataset (real distributions + synthetic labels)

## Days 3–4 — Stage 1: Diagnosis (ML Classifier)
- [ ] Day 3: Feature engineering — encode decline code, retry count, amount, time features, customer history
- [ ] Day 3: Train/test split (80/20), held out and untouched until evaluation
- [ ] Day 4: Train Random Forest / XGBoost multi-class classifier
- [ ] Day 4: Generate confusion matrix, per-class precision/recall, feature importance chart
- [ ] Day 4: Wire diagnosis output into FastAPI endpoint + audit log

## Days 5–6 — Stage 2: Retry Sequencer (ML Model)
- [ ] Day 5: Build candidate-window training rows (multiple windows per failed payment, simulated success outcome)
- [ ] Day 5: Train/test split; bake in 24-hour RBI pre-debit notice constraint
- [ ] Day 6: Train binary success-probability model
- [ ] Day 6: Implement hard stopping rule (max 4 retries / 30 days)
- [ ] Day 6: Run naive fixed-schedule baseline vs. model-picked windows on same test batch; save comparison

## Days 7–8 — Stage 3: Promise Tracker (Gemini LLM)
- [ ] Day 7: Get free Gemini API key from Google AI Studio; add to `.env`
- [ ] Day 7: Build `extract_promise()` — structured JSON extraction from simulated customer replies
- [ ] Day 8: Build pause/re-check logic tied to promised date
- [ ] Day 8: Build trust-adjusted escalation (stricter cadence for AI-made promises, per Yale study rationale)
- [ ] Day 8: Wire into FastAPI endpoint + audit log

## Days 9–11 — Frontend (React) + Full Wiring
- [ ] Day 9: Set up Vite + React + Tailwind project; build FastAPI endpoints serving dashboard JSON
- [ ] Day 10: Build Overview page (headline metrics) + Stage 2 comparison chart (Recharts)
- [ ] Day 11: Build Stage 1 confusion matrix view + Stage 3 promise funnel + searchable audit trail table
- [ ] Day 11: Connect all pages to live backend; handle loading/error states

## Day 12 — Testing + "What Broke" Story
- [ ] Run full pipeline end-to-end against the real React frontend
- [ ] Fix real bugs found; log each one in `CHANGELOG_ISSUES.md` as it happens
- [ ] Re-verify every dashboard number is reproducible from a clean run

## Day 13 — Documentation
- [ ] Finalize architecture.md with any changes made during the build
- [ ] Write GitHub README (setup instructions, screenshots, architecture summary)
- [ ] Finalize `CHANGELOG_ISSUES.md` into the "what broke and how it was fixed" narrative

## Day 14 — Pitch Video + Buffer
- [ ] Script and record the 5-minute pitch (problem → architecture → real metrics → RBI-compliance angle → Yale-study design choice → what broke)
- [ ] Use remaining time as buffer for last-minute fixes
- [ ] Final GitHub repo cleanup and submission

---

## Optional Stage 4 — Hinglish Voice Recovery (ONLY after Day 14's core is fully working)
1. Add a voice-trigger condition (customer unresponsive after 2 text attempts)
2. Build simple Hinglish message templates for an IVR-style flow
3. Build basic response capture (key-press or simple speech-to-text)
4. Map the captured response into the same promise-tracker schema used in Stage 3
5. Test with a handful of simulated calls
6. Log everything into the same audit trail as the other channels

---

## Known tight spot (flagged honestly)
Days 9–11 (React build) compressed the original dedicated buffer day into Day 14. If the React build runs long, protect Days 3–6 (the ML work) first — that's the project's core differentiation. Dashboard polish and documentation can flex; the ML story cannot.
