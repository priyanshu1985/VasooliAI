from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# -------------------------------------------------------------
# Overview Schemas
# -------------------------------------------------------------
class FunnelMetrics(BaseModel):
    failed: int = Field(..., description="Total failed payments entering pipeline")
    retried: int = Field(..., description="Payments scheduled for smart retry")
    recovered: int = Field(..., description="Payments successfully recovered")
    promise_tracked: int = Field(..., description="Payments escalated to Stage 3 Promise Tracker")
    closed: int = Field(..., description="Payments stopped under compliance caps")


class OverviewResponse(BaseModel):
    total_payments: int = Field(..., description="Total batch volume processed")
    total_recovered: float = Field(..., description="Total money recovered in INR")
    recovery_rate: float = Field(..., description="Overall recovery rate percentage")
    diagnosis_accuracy: float = Field(..., description="Stage 1 classification accuracy percentage")
    funnel: FunnelMetrics


# -------------------------------------------------------------
# Stage 1 Schemas
# -------------------------------------------------------------
class FeatureImportanceItem(BaseModel):
    feature: str = Field(..., description="Feature column name")
    importance: float = Field(..., description="Normalized Gini importance score")


class Stage1MetricsResponse(BaseModel):
    labels: List[str] = Field(..., description="Actionable failure class names")
    confusion_matrix: List[List[int]] = Field(..., description="Actual vs predicted confusion matrix")
    accuracy: float = Field(..., description="Held-out test set accuracy percentage")
    feature_importance: List[FeatureImportanceItem] = Field(..., description="Ranked feature importances")
    takeaway: str = Field(..., description="Plain-language interpretation of findings")


# -------------------------------------------------------------
# Stage 2 Schemas
# -------------------------------------------------------------
class Stage2MetricsResponse(BaseModel):
    naive_recovery_rate: float = Field(..., description="Recovery rate under fixed 24h schedule")
    smart_recovery_rate: float = Field(..., description="Recovery rate under ML-picked windows")
    recovery_lift_pct: float = Field(..., description="Percentage lift achieved over naive baseline")
    stopping_rule_violations: int = Field(0, description="Violations of 4-retry cap (must be 0)")
    rbi_notice_violations: int = Field(0, description="Violations of 24h notice window (must be 0)")
    max_retries_cap_enforced: int = Field(4, description="Configured stopping rule cap")
    takeaway: str = Field(..., description="Plain-language summary of Stage 2 lift")


# -------------------------------------------------------------
# Stage 3 Schemas
# -------------------------------------------------------------
class EscalationFunnelMetrics(BaseModel):
    gentle_reminder: int = Field(..., description="Step 1 gentle text notifications")
    firmer_nudge: int = Field(..., description="Step 2 firmer advisory notice")
    final_notice: int = Field(..., description="Step 3 impending cancellation alert")
    stopped: int = Field(..., description="Step 4 outreach terminated under anti-harassment rule")


class Stage3MetricsResponse(BaseModel):
    promises_kept: int = Field(..., description="Commitments fulfilled on promised date")
    promises_broken: int = Field(..., description="Broken commitments escalated through ladder")
    promise_kept_rate: float = Field(..., description="Percentage of promises fulfilled")
    escalation_funnel: EscalationFunnelMetrics
    takeaway: str = Field(..., description="Plain-language takeaway from Yale study escalation")


class ExtractPromiseRequest(BaseModel):
    customer_reply: str = Field(..., description="Freeform customer response text to analyze", min_length=1)


class ExtractPromiseResponse(BaseModel):
    is_promise: bool = Field(..., description="Whether a concrete payment commitment was extracted")
    promised_date: Optional[str] = Field(None, description="ISO date YYYY-MM-DD or null")
    promised_amount: Optional[float] = Field(None, description="Committed payment amount in INR or null")
    confidence: float = Field(..., description="Extraction confidence score (0.0 - 1.0)")
    reasoning: str = Field(..., description="Model explanation for parsing result")
    model_used: Optional[str] = Field(None, description="Gemini model or fallback parser name")
    _is_fallback: Optional[bool] = None


# -------------------------------------------------------------
# Audit Trail Schemas
# -------------------------------------------------------------
class AuditLogRow(BaseModel):
    timestamp: str
    stage: str
    payment_id: str
    decision: str
    reasoning: str
    outcome: Optional[str] = None


class AuditTrailResponse(BaseModel):
    rows: List[AuditLogRow]
    total_count: int


class PipelineRunResponse(BaseModel):
    status: str
    message: str
    overview: OverviewResponse
