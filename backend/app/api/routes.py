import os
import json
from fastapi import APIRouter, Depends, Query, Body, HTTPException, Request, Header
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import AuditLog
from app.pipeline_runner import get_pipeline_results, run_pipeline_batch
from app.stage3_promise.extractor import extract_promise, _get_gemini_client
from app.webhook.razorpay import verify_razorpay_signature, process_razorpay_webhook_event
from app.api.schemas import (
    OverviewResponse,
    Stage1MetricsResponse,
    Stage2MetricsResponse,
    Stage3MetricsResponse,
    AuditTrailResponse,
    PipelineRunResponse,
    ExtractPromiseRequest,
    ExtractPromiseResponse,
    AuditAskRequest,
    AuditAskResponse
)

# Illustrative estimated average cost per retry attempt in INR (illustrative estimate, not a real fee schedule)
ASSUMED_COST_PER_RETRY_INR = 5.0

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/overview", response_model=OverviewResponse)
def get_overview_metrics(db: Optional[Session] = Depends(get_db)):
    """
    Overview endpoint serving headline recovery metrics, pipeline funnel,
    and computed cost savings from avoiding bad retries on fraud/risk flagged payments.
    Data Contract per docs/design.md section 5.
    """
    pipeline_data = get_pipeline_results()
    overview_data = dict(pipeline_data["overview"])

    # Count Stage 1 risk_fraud_flag payments (correctly identified as NOT worth retrying)
    risk_fraud_count = 0
    if db is not None:
        try:
            db_risk_count = db.query(AuditLog).filter(
                AuditLog.stage == "stage1",
                AuditLog.decision.ilike("%risk_fraud_flag%")
            ).count()
            if db_risk_count > 0:
                risk_fraud_count = db_risk_count
        except Exception:
            pass

    if risk_fraud_count == 0 and "audit" in pipeline_data:
        audit_rows = pipeline_data.get("audit", {}).get("rows", [])
        risk_fraud_count = sum(
            1 for row in audit_rows
            if row.get("stage") == "stage1" and "risk_fraud_flag" in str(row.get("decision", ""))
        )

    money_saved = round(risk_fraud_count * ASSUMED_COST_PER_RETRY_INR, 2)
    overview_data["money_saved_avoiding_retries"] = money_saved
    overview_data["risk_fraud_avoided_count"] = risk_fraud_count

    return overview_data


@router.get("/stage1", response_model=Stage1MetricsResponse)
def get_stage1_metrics():
    """
    Stage 1 Diagnosis metrics endpoint: evaluated confusion matrix, labels, and feature importance.
    Data Contract per docs/design.md section 5.
    """
    pipeline_data = get_pipeline_results()
    return pipeline_data["stage1"]


@router.get("/stage2", response_model=Stage2MetricsResponse)
def get_stage2_metrics():
    """
    Stage 2 Retry Sequencer metrics: naive vs. smart recovery comparison & stopping rules.
    Data Contract per docs/design.md section 5.
    """
    pipeline_data = get_pipeline_results()
    return pipeline_data["stage2"]


@router.get("/stage3", response_model=Stage3MetricsResponse)
def get_stage3_metrics():
    """
    Stage 3 Promise Tracker metrics: promise adherence and escalation ladder funnel.
    Data Contract per docs/design.md section 5.
    """
    pipeline_data = get_pipeline_results()
    return pipeline_data["stage3"]


@router.get("/audit", response_model=AuditTrailResponse)
def get_audit_trail(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    stage: Optional[str] = None,
    search: Optional[str] = None,
    db: Optional[Session] = Depends(get_db)
):
    """
    Audit Trail endpoint returning searchable/sortable historical decision rows.
    Data Contract per docs/design.md section 5.
    """
    if db is not None:
        try:
            query = db.query(AuditLog)
            if stage:
                query = query.filter(AuditLog.stage == stage)
            if search:
                query = query.filter(AuditLog.payment_id.ilike(f"%{search}%") | AuditLog.decision.ilike(f"%{search}%"))
            total_count = query.count()
            db_rows = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
            
            if total_count > 0:
                formatted_rows = [
                    {
                        "timestamp": row.timestamp.isoformat() if row.timestamp else "",
                        "stage": row.stage,
                        "payment_id": row.payment_id,
                        "decision": row.decision,
                        "reasoning": str(row.reasoning_inputs),
                        "outcome": row.outcome
                    }
                    for row in db_rows
                ]
                return {
                    "rows": formatted_rows,
                    "total_count": total_count
                }
        except Exception:
            pass

    pipeline_data = get_pipeline_results()
    all_rows = pipeline_data["audit"]["rows"]

    filtered_rows = all_rows
    if stage:
        filtered_rows = [r for r in filtered_rows if r.get("stage") == stage]
    if search:
        search_lower = search.lower()
        filtered_rows = [
            r for r in filtered_rows
            if search_lower in r.get("payment_id", "").lower()
            or search_lower in r.get("decision", "").lower()
            or search_lower in r.get("reasoning", "").lower()
        ]

    return {
        "rows": filtered_rows[offset:offset + limit],
        "total_count": len(filtered_rows)
    }


@router.post("/audit/ask", response_model=AuditAskResponse)
def ask_audit_trail(
    payload: AuditAskRequest = Body(...),
    db: Optional[Session] = Depends(get_db)
):
    """
    Plain-English QA over the decision audit log powered by Gemini LLM.
    Answers questions strictly using logged historical decisions.
    """
    question = payload.question.strip()
    payment_id = payload.payment_id.strip() if payload.payment_id else None

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    rows = []
    if db is not None:
        try:
            query = db.query(AuditLog)
            if payment_id:
                query = query.filter(AuditLog.payment_id.ilike(f"%{payment_id}%"))
            db_rows = query.order_by(AuditLog.timestamp.desc()).limit(30).all()
            for r in db_rows:
                rows.append({
                    "timestamp": r.timestamp.isoformat() if r.timestamp else "",
                    "stage": r.stage,
                    "payment_id": r.payment_id,
                    "decision": r.decision,
                    "reasoning": str(r.reasoning_inputs),
                    "outcome": r.outcome or ""
                })
        except Exception:
            pass

    if not rows:
        pipeline_data = get_pipeline_results()
        cached_rows = pipeline_data.get("audit", {}).get("rows", [])
        if payment_id:
            rows = [r for r in cached_rows if payment_id.lower() in str(r.get("payment_id", "")).lower()][:30]
        else:
            rows = cached_rows[:30]

    if not rows:
        return AuditAskResponse(
            question=question,
            answer="No audit log entries were found matching your criteria to answer this question.",
            rows_analyzed=0,
            model_used="none"
        )

    formatted_lines = []
    for r in rows:
        formatted_lines.append(
            f"- [{r.get('timestamp', '')}] Stage: {r.get('stage', '')} | Payment: {r.get('payment_id', '')} | "
            f"Decision: {r.get('decision', '')} | Outcome: {r.get('outcome', '')} | Reasoning: {r.get('reasoning', '')}"
        )
    formatted_data = "\n".join(formatted_lines)

    prompt = (
        f"Given these logged decisions:\n{formatted_data}\n\n"
        f"Answer this question in one or two plain-English sentences:\n{question}\n\n"
        f"Only use the data given, do not invent details not present in the log."
    )

    answer = None
    model_used = None

    client = _get_gemini_client()
    if client is not None:
        candidate_models = ["gemini-3.6-flash", "gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-pro-latest"]
        for m_name in candidate_models:
            try:
                model = client.GenerativeModel(m_name)
                resp = model.generate_content(prompt)
                if resp and resp.text:
                    answer = resp.text.strip()
                    model_used = m_name
                    break
            except Exception:
                continue

    if not answer:
        model_used = "audit-summary-fallback"
        stages = set(r.get("stage") for r in rows)
        outcomes = [r.get("outcome") for r in rows if r.get("outcome")]
        sample_decision = rows[0].get("decision", "") if rows else ""
        answer = f"Analyzed {len(rows)} logged audit events across {', '.join(stages)}. Latest decision: {sample_decision}."

    return AuditAskResponse(
        question=question,
        answer=answer,
        rows_analyzed=len(rows),
        model_used=model_used
    )


@router.post("/pipeline/run", response_model=PipelineRunResponse)
def trigger_pipeline_run(
    limit: int = Query(default=300, ge=10, le=1200),
    db: Optional[Session] = Depends(get_db)
):
    """
    Triggers an end-to-end batch processing run through Stages 1, 2, and 3.
    """
    results = run_pipeline_batch(db=db, limit=limit)
    return {
        "status": "success",
        "message": f"Processed {results['overview']['total_payments']} failed payments across Stages 1, 2, and 3.",
        "overview": results["overview"]
    }


@router.post("/stage3/extract-promise", response_model=ExtractPromiseResponse)
def live_extract_promise(payload: ExtractPromiseRequest):
    """
    Live interactive test endpoint: parses any customer reply text with Google Gemini LLM.
    """
    if not payload.customer_reply.strip():
        raise HTTPException(status_code=400, detail="Customer reply text cannot be empty.")
    return extract_promise(payload.customer_reply)


@router.post("/webhook/razorpay", tags=["webhook"])
async def razorpay_webhook_endpoint(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None, alias="X-Razorpay-Signature"),
    db: Optional[Session] = Depends(get_db)
):
    """
    Razorpay Webhook receiver for live payment/subscription degradation events.
    1. Authenticates webhook with HMAC-SHA256 signature verification.
    2. Ingests payload and triggers multi-stage recovery pipeline.
    3. Streams immutable decision records to audit trail with tag 'razorpay_webhook'.
    4. Returns 200 OK immediately to satisfy gateway SLA.
    """
    raw_body = await request.body()
    signature = (
        x_razorpay_signature
        or request.headers.get("x-razorpay-signature")
        or request.headers.get("X-Razorpay-Signature")
    )
    webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")

    # Verify signature
    if not verify_razorpay_signature(raw_body, signature, webhook_secret):
        raise HTTPException(
            status_code=400,
            detail="Invalid or missing Razorpay webhook signature."
        )

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON webhook payload.")

    result = process_razorpay_webhook_event(payload, db=db)
    return {
        "status": "success",
        "message": "Razorpay event ingested and processed through recovery pipeline.",
        "result": result
    }
