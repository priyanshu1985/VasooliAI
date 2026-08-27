from datetime import datetime
from typing import Any, Dict, Optional
import logging
from sqlalchemy.orm import Session
from app.db.models import AuditLog

logger = logging.getLogger("recovery_ai.audit")


def log_audit_event(
    db: Optional[Session],
    stage: str,
    payment_id: str,
    decision: str,
    reasoning_inputs: Dict[str, Any],
    outcome: Optional[str] = None
) -> Dict[str, Any]:
    """
    Writes a decision and reasoning event to the immutable audit_log table.

    Required fields:
      - stage: 'stage1', 'stage2', 'stage3', or 'system'
      - payment_id: unique transaction identifier
      - decision: short summary of action taken
      - reasoning_inputs: JSON dict of model inputs / rules checked
      - outcome: result or status (e.g. 'scheduled', 'success', 'stopped')
    """
    event_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "stage": stage,
        "payment_id": payment_id,
        "decision": decision,
        "reasoning_inputs": reasoning_inputs,
        "outcome": outcome
    }

    if db is not None:
        try:
            audit_entry = AuditLog(
                timestamp=datetime.utcnow(),
                stage=stage,
                payment_id=str(payment_id),
                decision=decision,
                reasoning_inputs=reasoning_inputs,
                outcome=outcome
            )
            db.add(audit_entry)
            db.commit()
            db.refresh(audit_entry)
            event_data["id"] = audit_entry.id
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to persist audit log to database: {e}")

    logger.info(f"[AUDIT] [{stage.upper()}] Payment: {payment_id} | Decision: {decision} | Outcome: {outcome}")
    return event_data
