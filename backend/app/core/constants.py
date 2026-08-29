"""
Core regulatory, architectural, and business constants for the RecoveryAI platform.
Single source of truth for constraints enforced across all stages.
"""

# Regulatory constraint: RBI Digital Payments - E-Mandate Framework 2026
# Mandatory pre-debit advisory notification window (in hours)
RBI_MIN_NOTICE_HOURS: int = 24

# Regulatory & operational constraint: Maximum retry attempts in rolling 30-day window
MAX_RETRIES_PER_30_DAYS: int = 4

# Candidate retry windows in hours from initial failure
DEFAULT_CANDIDATE_WINDOWS_HOURS: list[int] = [24, 36, 72, 168]

# Yale Study (Prof. James Choi) Calibrated Escalation Ladder Stages
# Tighter follow-up cadence for AI-solicited commitments
ESCALATION_STAGES: list[str] = [
    "gentle_reminder",
    "firmer_nudge",
    "final_notice",
    "stopped"
]

# Actionable decline classes produced by Stage 1 ML Classifier
STAGE1_CLASSES: list[str] = [
    "card_expired",
    "insufficient_funds_or_technical",
    "risk_fraud_flag"
]
