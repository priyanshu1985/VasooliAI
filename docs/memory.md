# Memory.md
## Persistent project context for any AI coding assistant

Read this file at the start of every coding session on this project. It captures decisions that were already debated and locked — do not re-litigate them without a clear new reason, and if you do change one, update this file in the same change.

---

## Project identity
- Razorpay AI Buildathon 2026, **AI Revenue Recovery** track
- Timeline: 14 days total
- Goal: get shortlisted for a panel interview by submitting a working GitHub repo, 5-minute pitch video, and architecture doc

## Locked scope decision
- The project combines **3 of Razorpay's 7 example directions** into one chained pipeline, not 3 separate features:
  1. Failed-Subscription Recovery (diagnose)
  2. Mandate Retry Sequencer (decide + act)
  3. Promise-to-Pay Tracker (close the loop)
- **Hinglish Voice Recovery** is an approved **optional Stage 4** — attempt only after Stages 1–3 fully work end-to-end. Do not let it consume time from the core 3.

## Locked technical decisions (with the "why," so they aren't accidentally reversed)

1. **Stage 1 and Stage 2 use trained ML models (scikit-learn/XGBoost), not LLM calls.**
   Why: a judge asking "what AI did you actually build?" deserves a defensible answer backed by a confusion matrix and feature importance — not "we called an API." This was a deliberate correction made mid-planning after review.

2. **Stage 3 uses an LLM (Google Gemini API, free tier).**
   Why: extracting a promise from freeform customer text needs real language understanding; training a classical model for this would need thousands of labeled real conversations that don't exist for this project. This is the one stage where LLM use is the *correct* choice, not a shortcut — and that distinction should be stated explicitly in the pitch.

3. **Data strategy is hybrid: real Kaggle transaction dataset (for realistic amount/timing structure) + Faker-generated synthetic labels (decline reason, retry outcome) layered on top.**
   Why: no public dataset exists with subscription-failure decline-reason + retry-outcome labels (this is proprietary business data). Full synthetic data alone would look "too fake"; this hybrid grounds the data in something real while still allowing controlled ground-truth accuracy testing.

4. **Database is PostgreSQL via Supabase (free tier), not SQLite.**
   Why: SQLite is a local file; most deployment platforms wipe local files on redeploy. This was caught and corrected before deployment, not after.

5. **Frontend is React (Vite) + Tailwind + Recharts, not Streamlit.**
   Why: the user explicitly wants a production-level system, not a quick internal tool. The lightweight setup (Vite, no custom CSS, one charting library) was chosen specifically to keep this real but fast to build within the 14-day window.

6. **No confirmed Razorpay API credit program exists for this specific submission-based buildathon** (a separate in-person GrowthX hackathon did offer credits, but that's a different event) — so all LLM costs are covered by Google Gemini's genuinely free, no-card-required tier.

## Research grounding baked into the design (cite these in the pitch — they are differentiators)
- **RBI Digital Payments – E-Mandate Framework, 2026** (effective 22 April 2026): 24-hour pre-debit notice requirement, ₹15,000 AFA-free threshold (₹1 lakh for SIPs/insurance/credit cards). Stage 2's retry timing logic must never violate the 24-hour notice window.
- **Yale study (Prof. James Choi) on AI vs. human debt collectors:** AI-made promises are broken more often than human-made ones; AI collectors recovered ~9% less in the first 30 days. Stage 3 deliberately applies a stricter follow-up cadence *because* the promise was AI-solicited — this is a designed-in response to a known real-world weakness, not an oversight.
- Full source list lives in the research PDF generated earlier in the project (existing solutions: Stripe Smart Retries, Recurly Intelligent Retries, Skit.ai, IRIS Insights Promise Keeper, AgentCollect).

## Things NOT to reintroduce
- SQLite (replaced by Postgres — do not fall back to it for "simplicity")
- Streamlit (replaced by React — do not suggest it as a shortcut)
- Hardcoded if-else logic disguised as "diagnosis" or "decision-making" in Stages 1–2 (must be real trained models)
- Unbounded retry loops or unbounded promise-follow-up loops (hard stopping rules are load-bearing, not optional)

## Where the full detail lives
- Product scope and success metrics → `prd.md`
- Full system design and data flow → `architecture.md`
- Coding constraints and do/don't rules → `rules.md`
- Day-by-day task checklist → `plan.md`
- Dashboard UI/UX spec → `design.md`
- ML dataset combination + training pipeline → `ml/README.md` and accompanying scripts
