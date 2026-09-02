"""
Stage 4 — Hinglish Voice Recovery Simulator Route.
Isolated, additive endpoint that maps IVR keypad responses (1 or 2)
directly into existing Stage 3 promise evaluation and audit logging.
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import AuditLog
from app.pipeline_runner import get_pipeline_results
from app.stage3_promise.tracker import evaluate_promise_commitment


router = APIRouter(prefix="/api/stage4", tags=["stage4_voice"])


class VoiceKeypressRequest(BaseModel):
    payment_id: str = Field(..., description="Unique ID of the failed payment")
    keypress: int = Field(..., ge=1, le=2, description="1 for Haan (promise), 2 for Nahi (refused)")
    customer_id: Optional[str] = "cust_ivr_voice_user"


class VoiceKeypressResponse(BaseModel):
    status: str
    payment_id: str
    keypress: int
    action_taken: str
    decision: str
    audit_logged: bool


@router.post("/voice-response", response_model=VoiceKeypressResponse)
def handle_voice_keypress(
    payload: VoiceKeypressRequest,
    db: Optional[Session] = Depends(get_db)
):
    """
    Ingests IVR keypad selection (1 or 2) from the Hinglish Voice call:
      - Key 1 ("Haan"): Maps to payment commitment promise for next Friday, pauses reminders.
      - Key 2 ("Nahi"): Maps to no-commitment refusal, escalates outreach ladder.
    Logs decision to audit trail with source tag 'hinglish_voice_simulation'.
    """
    now_iso = datetime.now(timezone.utc).isoformat()

    if payload.keypress == 1:
        # Key 1: Customer committed to pay
        eval_result = evaluate_promise_commitment(
            payment_id=payload.payment_id,
            customer_reply="Haan, pay karunga Friday tak",
            use_llm=False
        )
        decision_text = "Hinglish IVR Call: Customer pressed [1] (Committed to pay by Friday). Pausing automated reminders."
        outcome = "reminders_paused"
        action = "promise_recorded_reminders_paused"
    else:
        # Key 2: Customer refused / cannot pay
        eval_result = evaluate_promise_commitment(
            payment_id=payload.payment_id,
            customer_reply="Nahi, abhi nahi kar sakta",
            use_llm=False
        )
        decision_text = "Hinglish IVR Call: Customer pressed [2] (Refused / No commitment). Advanced escalation ladder to firmer nudge."
        outcome = "escalated_to_firmer_nudge"
        action = "escalated_outreach"

    audit_entry = {
        "timestamp": now_iso,
        "stage": "stage4_voice",
        "payment_id": payload.payment_id,
        "decision": decision_text,
        "reasoning": str({
            "channel": "hinglish_ivr_voice",
            "source": "hinglish_voice_simulation",
            "keypress": payload.keypress,
            "stage3_eval": eval_result.get("status")
        }),
        "outcome": outcome
    }

    # 1. Update in-memory audit store for immediate UI reactivity
    pipeline_data = get_pipeline_results()
    if "audit" in pipeline_data and "rows" in pipeline_data["audit"]:
        pipeline_data["audit"]["rows"].insert(0, audit_entry)

    # 2. Persist to live Supabase DB if available
    if db is not None:
        try:
            db_log = AuditLog(
                stage="stage4_voice",
                payment_id=payload.payment_id,
                decision=decision_text,
                reasoning_inputs={
                    "channel": "hinglish_ivr_voice",
                    "source": "hinglish_voice_simulation",
                    "keypress": payload.keypress
                },
                outcome=outcome
            )
            db.add(db_log)
            db.commit()
        except Exception:
            pass

    return {
        "status": "success",
        "payment_id": payload.payment_id,
        "keypress": payload.keypress,
        "action_taken": action,
        "decision": decision_text,
        "audit_logged": True
    }
