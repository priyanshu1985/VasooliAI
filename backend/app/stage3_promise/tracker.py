from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from app.core.constants import ESCALATION_STAGES
from app.stage3_promise.extractor import extract_promise


def get_next_escalation_stage(current_stage: str) -> str:
    """Calculates the next stage in the escalation ladder."""
    try:
        idx = ESCALATION_STAGES.index(current_stage)
        if idx < len(ESCALATION_STAGES) - 1:
            return ESCALATION_STAGES[idx + 1]
        return "stopped"
    except ValueError:
        return "gentle_reminder"


def evaluate_promise_commitment(
    payment_id: str,
    customer_reply: str,
    current_escalation_stage: str = "gentle_reminder",
    customer_past_broken_promises: int = 0,
    use_llm: bool = False
) -> Dict[str, Any]:
    """
    Evaluates a freeform customer outreach response, extracts promise terms with Gemini LLM (or fast rule extractor for batch),
    and applies Yale-study calibrated trust adjustments and pause logic.

    Yale-Study Rationale:
      - AI-collected debts suffer from lower commitment adherence.
      - If a customer has previously broken promises, or if the extracted promise confidence is low,
        the follow-up cadence is tightened.
    """
    if use_llm:
        extraction = extract_promise(customer_reply)
    else:
        from app.stage3_promise.extractor import extract_promise_rule_fallback
        extraction = extract_promise_rule_fallback(customer_reply)
    is_promise = extraction.get("is_promise", False)
    promised_date = extraction.get("promised_date")
    promised_amount = extraction.get("promised_amount")
    confidence = extraction.get("confidence", 0.8)
    reasoning = extraction.get("reasoning", "")

    if is_promise and promised_date:
        # Trust score calculation: penalize past broken promises
        trust_score = max(0.2, round(confidence - (customer_past_broken_promises * 0.15), 2))
        
        # Determine pause window
        decision_text = f"Payment commitment detected for {promised_date}. Reminders paused."
        outcome = "reminders_paused"
        status = "pending"
        next_stage = current_stage if (current_stage := current_escalation_stage) in ESCALATION_STAGES else "gentle_reminder"
    else:
        # No commitment or refusal: advance escalation ladder
        next_stage = get_next_escalation_stage(current_escalation_stage)
        trust_score = 0.10
        status = "broken" if customer_past_broken_promises > 0 else "no_promise"
        if next_stage == "stopped":
            decision_text = "Outreach limit reached without commitment. Escalation stopped to prevent harassment."
            outcome = "stopped"
        else:
            decision_text = f"No concrete payment promise extracted. Advanced escalation ladder to '{next_stage}'."
            outcome = f"escalated_to_{next_stage}"

    return {
        "payment_id": payment_id,
        "is_promise": is_promise,
        "promised_date": promised_date,
        "promised_amount": promised_amount,
        "confidence": confidence,
        "trust_score": trust_score,
        "status": status,
        "escalation_stage": next_stage,
        "decision": decision_text,
        "outcome": outcome,
        "reasoning": f"LLM reasoning: '{reasoning}'. Past broken promises: {customer_past_broken_promises}, trust score: {trust_score}",
        "raw_reply": customer_reply
    }
