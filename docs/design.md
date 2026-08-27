# Design.md
## Dashboard UI/UX — AI Revenue Recovery Agent

Stack: React (Vite) + Tailwind CSS + Recharts

---

## 1. Design Principles

- **Numbers first, decoration second.** Judges are evaluating proof, not visual flair — every page should lead with a real metric, not an illustration.
- **Every chart must have a plain-language takeaway line under it** (e.g., "Smart retries recovered 23% more than fixed-schedule retries on this batch") — never leave a judge to interpret a chart alone.
- **Keep it to 4 pages.** More pages = more build time for no added credibility. Depth per page beats breadth of pages.

## 2. Pages

### Page 1 — Overview
- Header metric cards (4 across): Total Payments Processed, Total Money Recovered, Overall Recovery Rate %, Diagnosis Accuracy %
- Below: a simple funnel visual — Failed → Retried → Recovered / Promise Tracked → Closed
- Purpose: this is the page a judge sees first — it must answer "did this work?" in under 5 seconds

### Page 2 — Stage 1: Diagnosis
- Confusion matrix (heatmap, Recharts or a simple table with color intensity)
- Feature importance horizontal bar chart
- One-line takeaway: e.g., "Retry count and decline code were the strongest predictors of failure type"

### Page 3 — Stage 2: Retry Sequencer
- Side-by-side bar chart: Naive fixed-schedule recovery rate vs. Smart model-picked recovery rate
- A small table showing the stopping-rule enforcement (e.g., "0 payments exceeded the 4-retry cap")
- One-line takeaway on the real lift %

### Page 4 — Stage 3: Promise Tracker + Audit Trail
- Promise-kept vs. broken donut/bar chart
- Escalation funnel (gentle reminder → firmer nudge → final notice → stopped)
- Below: a searchable/filterable audit trail table — columns: timestamp, stage, payment ID, decision, reasoning summary, outcome

## 3. Visual Style

- **Color use is functional, not decorative:** green for recovered/success, amber for pending/in-progress, red for broken promises/hard declines, neutral gray for stopped/closed states. Don't introduce extra colors beyond this palette.
- **Typography:** one clean sans-serif font (Tailwind's default `font-sans` is fine) — don't spend time picking custom fonts.
- **Layout:** simple top navigation bar with the 4 page names; content area uses a card-based grid (Tailwind `grid` + `rounded-xl` cards with subtle shadow) — this alone looks production-clean without custom CSS work.
- **No animations or transitions needed** — this is not the place to spend limited build time.

## 4. Component List (for the AI coding assistant to scaffold)

- `MetricCard.jsx` — reusable stat card (label, value, optional delta)
- `ComparisonBarChart.jsx` — reusable naive-vs-smart bar chart (Recharts)
- `ConfusionMatrix.jsx` — grid-based heatmap component
- `FeatureImportanceChart.jsx` — horizontal bar chart (Recharts)
- `EscalationFunnel.jsx` — simple stacked funnel visual
- `AuditTrailTable.jsx` — searchable/sortable table with pagination
- `NavBar.jsx` — top navigation across the 4 pages

## 5. Data Contract (what the backend must serve)

Each page's components expect a single JSON payload from its matching FastAPI endpoint, e.g.:

```
GET /api/overview        -> { total_payments, total_recovered, recovery_rate, diagnosis_accuracy, funnel: {...} }
GET /api/stage1          -> { confusion_matrix: [[...]], labels: [...], feature_importance: [{feature, importance}] }
GET /api/stage2          -> { naive_recovery_rate, smart_recovery_rate, stopping_rule_violations: 0 }
GET /api/stage3          -> { promises_kept, promises_broken, escalation_funnel: {...} }
GET /api/audit           -> { rows: [{timestamp, stage, payment_id, decision, reasoning, outcome}], total_count }
```

Keep this contract stable — if the AI coding assistant changes a field name in the backend, it must update the corresponding frontend component in the same change.
