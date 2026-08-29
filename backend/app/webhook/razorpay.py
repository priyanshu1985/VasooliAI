import hmac
import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.pipeline_runner import process_single_payment

logger = logging.getLogger("recovery_ai.webhook")


def verify_razorpay_signature(
    raw_body: bytes,
    signature: Optional[str],
    webhook_secret: Optional[str]
) -> bool:
    """
    Verifies the webhook signature sent by Razorpay in the X-Razorpay-Signature header.
    Per Razorpay docs: HMAC-SHA256 of raw request body using the configured webhook secret.
    Uses constant-time comparison to prevent timing attacks.
    """
    if not webhook_secret:
        logger.warning("[Webhook] RAZORPAY_WEBHOOK_SECRET is missing or empty in backend/.env.")
        return False

    if not signature:
        logger.warning("[Webhook] Incoming request is missing the X-Razorpay-Signature header.")
        return False

    expected_signature = hmac.new(
        key=webhook_secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    is_valid = hmac.compare_digest(expected_signature, signature.strip())
    if not is_valid:
        logger.warning(f"[Webhook] Signature mismatch. Received: {signature[:12]}...")
    return is_valid


def process_razorpay_webhook_event(
    event_payload: Dict[str, Any],
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Parses a verified Razorpay webhook payload and feeds failed payments into the recovery pipeline.
    Supported events: subscription.pending, payment.failed, subscription.charged, etc.
    """
    event_type = event_payload.get("event", "unknown")
    payload_data = event_payload.get("payload", {})
    
    # Extract entity from either payment or subscription payload container
    payment_entity = payload_data.get("payment", {}).get("entity", {})
    subscription_entity = payload_data.get("subscription", {}).get("entity", {})

    # Extract payment/subscription ID
    payment_id = (
        payment_entity.get("id")
        or subscription_entity.get("id")
        or f"pay_rzp_{int(datetime.now(timezone.utc).timestamp())}"
    )

    # Razorpay represents amounts in paise (1 INR = 100 paise)
    raw_amount_paise = payment_entity.get("amount") or subscription_entity.get("current_amount") or 150000
    amount_inr = float(raw_amount_paise) / 100.0

    # Extract failure attributes
    error_code = payment_entity.get("error_code") or payment_entity.get("error_reason") or "insufficient_funds"
    error_desc = payment_entity.get("error_description") or "Subscription debit failed at bank network."

    now_utc = datetime.now(timezone.utc)
    attempts = int(subscription_entity.get("charge_at", 0) or payment_entity.get("attempts", 0) or 1)

    # Map to Stage 1 Diagnosis feature schema
    features = {
        "amount": amount_inr / 85.0,  # Scaled to model training baseline
        "hour_of_day": now_utc.hour,
        "day_of_week": now_utc.weekday(),
        "retry_count_so_far": max(0, attempts - 1),
        "past_failure_count": int(payment_entity.get("past_failures", 0) or 0),
        "subscription_age_days": 45,  # Realistic default for active subscriptions
    }

    logger.info(f"[Webhook] Ingesting Razorpay event '{event_type}' for payment {payment_id} (₹{amount_inr:,.2f})")

    # Reuse the exact 3-stage pipeline chaining
    pipeline_result = process_single_payment(
        payment_id=payment_id,
        amount_inr=amount_inr,
        features=features,
        customer_reply=f"Payment {payment_id} failed: {error_desc}. Will retry shortly.",
        db=db,
        source="razorpay_webhook"
    )

    return {
        "status": "processed",
        "event": event_type,
        "payment_id": payment_id,
        "amount_inr": amount_inr,
        "pipeline_result": pipeline_result
    }
