import os
import json
from fastapi import APIRouter, Depends, Query, Body, HTTPException, Request, Header
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import AuditLog
from app.pipeline_runner import get_pipeline_results, run_pipeline_batch
from app.stage3_promise.extractor import extract_promise
from app.webhook.razorpay import verify_razorpay_signature, process_razorpay_webhook_event
from app.api.schemas import (
    OverviewResponse,
    Stage1MetricsResponse,
    Stage2MetricsResponse,
    Stage3MetricsResponse,
    AuditTrailResponse,
    PipelineRunResponse,
    ExtractPromiseRequest,
    ExtractPromiseResponse
)

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/overview", response_model=OverviewResponse)
def get_overview_metrics(db: Optional[Session] = Depends(get_db)):
    """
    Overview endpoint serving headline recovery metrics and pipeline funnel
    calculated from the live pipeline run.
    Data Contract per docs/design.md section 5.
    """
    pipeline_data = get_pipeline_results()
    return pipeline_data["overview"]


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
