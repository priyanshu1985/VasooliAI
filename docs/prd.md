# Product Requirements Document (PRD)
## Project: AI Revenue Recovery Agent — Razorpay AI Buildathon 2026

---

## 1. Problem Statement

Recurring payments fail constantly — expired cards, insufficient funds, bank timeouts, failed auto-debits. Most businesses handle this with dumb, fixed-schedule retries and generic reminder emails. This wastes money in two directions: retrying too often triggers bank fraud flags and penalties, while retrying too little or too late means recoverable money is written off as lost.

**Track:** AI Revenue Recovery (Razorpay AI Buildathon 2026)

**Core ask from Razorpay:** "Don't just identify the problem. Show measured money recovered across a batch, with compliant escalation, stopping rules, and an audit trail."

---

## 2. Goal

Build one chained recovery agent that takes a failed recurring payment through three connected stages, recovering as much real money as possible while respecting Indian payment regulations, and proving every decision with measurable numbers — not a demo that just "looks smart."

---

## 3. Scope — In and Out

### In scope (core, must complete)
1. **Stage 1 — Failed-Subscription Recovery (Diagnose):** classify why a payment failed
2. **Stage 2 — Mandate Retry Sequencer (Decide + Act):** pick the smartest retry timing
3. **Stage 3 — Promise-to-Pay Tracker (Close the loop):** capture and track customer commitments when retries fail

### Optional (Stage 4 — only after 1–3 are fully working)
4. **Hinglish Voice Recovery:** a simple IVR-style Hindi-English voice layer added on top of Stage 3, for customers unresponsive over text.

### Out of scope
- Real money movement — everything runs against synthetic/test-mode data, never live transactions
- A fully custom-trained NLP model for promise extraction (an LLM is used here deliberately — see architecture.md for why)
- Building a full merchant-facing SaaS product; this is a working proof-of-concept for a hiring buildathon, not a commercial launch

---

## 4. Users

- **Primary "user" for demo purposes:** a subscription-based merchant using Razorpay, whose recurring payments are failing and who wants revenue recovered automatically.
- **Real audience for this submission:** the Razorpay judging panel, who will read the GitHub repo, watch the 5-minute pitch video, and question the architecture directly.

---

## 5. Functional Requirements

### Stage 1 — Diagnose
- Given a failed payment's metadata (decline code, amount, retry count, time, customer history), output a predicted failure category with a confidence score
- Log every diagnosis, with reasoning inputs, to the audit trail

### Stage 2 — Decide + Act
- Given a diagnosed "retriable" failure, predict the best retry time window from a set of candidates
- Never schedule a retry inside the mandatory 24-hour RBI pre-debit notice window
- Enforce a hard stopping rule: max 4 retries within 30 days per payment
- Log every retry attempt and its outcome to the audit trail

### Stage 3 — Close the loop
- When retries are exhausted, simulate a customer outreach and capture a freeform reply
- Extract a promised payment date/amount from that reply using an LLM
- Pause reminders until the promised date, then auto re-check
- Track a per-customer "promise reliability" score; tighten follow-up cadence for customers who break promises
- Apply a stricter default cadence for AI-initiated promises specifically (see architecture.md — Yale study rationale)
- Log every promise, outcome, and escalation step to the audit trail

### Cross-cutting
- A dashboard (React) must show: total money recovered, recovery rate, Stage 1 confusion matrix + feature importance, Stage 2 naive-vs-smart comparison chart, Stage 3 promise-kept rate, and a searchable audit trail table

---

## 6. Non-Functional Requirements

- **Explainability:** every automated decision must be traceable to a logged reason — no black-box actions
- **Compliance-mindedness:** retry timing must respect the RBI 2026 e-mandate framework; messaging must never be harassing or infinite
- **Honesty of metrics:** all recovery/accuracy numbers must come from a real, reproducible run against the test batch — never a cherry-picked or invented figure
- **Deployability:** the app must survive a redeploy without losing data (hence Postgres, not SQLite)

---

## 7. Success Metrics (what "winning" looks like)

| Metric | Target for the demo |
|---|---|
| Stage 1 diagnosis accuracy | Report honestly from confusion matrix (aim 80%+, but report real number regardless) |
| Stage 2 recovery lift | Smart retry batch vs. naive fixed-schedule batch — show real % difference |
| Stage 3 promise-kept rate | Report honestly from simulated batch |
| Audit trail coverage | 100% of decisions logged and viewable in dashboard |
| Stopping-rule compliance | 0 payments retried beyond the hard cap in the test run |

---

## 8. Deliverables (per Razorpay's submission requirements)

1. Public GitHub repository with working code
2. 5-minute pitch video
3. Architecture document (see architecture.md)
4. A clear, honest account of what broke during development and how it was fixed

---

## 9. Key Risks

- **Time risk:** React frontend + ML training + LLM integration in ~14 days is tight — see plan.md for the day-by-day allocation and where buffer has been intentionally cut thin.
- **Credibility risk:** claiming inflated recovery numbers that mimic real production companies (70–85%) would look dishonest against a synthetic dataset — always frame numbers as a "directional proof of concept."
- **Scope creep risk:** Stage 4 (voice) must never be touched before Stages 1–3 are fully working end-to-end.
