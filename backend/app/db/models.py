from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


def utc_now():
    """Returns current UTC timestamp without timezone offset for naive DB columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    external_payment_id = Column(String(128), unique=True, index=True, nullable=False)
    customer_id = Column(String(128), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), default="INR", nullable=False)
    status = Column(String(32), default="failed", nullable=False)  # failed, recovered, promise_tracked, closed
    failure_code = Column(String(64), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    subscription_age_days = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    diagnoses = relationship("Diagnosis", back_populates="payment", cascade="all, delete-orphan")
    retries = relationship("Retry", back_populates="payment", cascade="all, delete-orphan")
    promises = relationship("Promise", back_populates="payment", cascade="all, delete-orphan")


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    predicted_reason = Column(String(64), nullable=False)
    confidence_score = Column(Float, nullable=False)
    input_features = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    payment = relationship("Payment", back_populates="diagnoses")


class Retry(Base):
    __tablename__ = "retries"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    retry_number = Column(Integer, nullable=False)
    scheduled_window_hours = Column(Integer, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    predicted_success_prob = Column(Float, nullable=False)
    outcome = Column(String(32), default="scheduled", nullable=False)  # scheduled, success, failed, skipped
    executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    payment = relationship("Payment", back_populates="retries")


class Promise(Base):
    __tablename__ = "promises"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(String(128), index=True, nullable=False)
    raw_reply_text = Column(Text, nullable=False)
    promised_date = Column(DateTime, nullable=True)
    promised_amount = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=False)
    status = Column(String(32), default="pending", nullable=False)  # pending, kept, broken, cancelled
    escalation_stage = Column(String(32), default="gentle_reminder", nullable=False)  # gentle_reminder, firmer_nudge, final_notice, stopped
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    payment = relationship("Payment", back_populates="promises")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True, nullable=False)
    stage = Column(String(32), index=True, nullable=False)  # stage1, stage2, stage3, system
    payment_id = Column(String(128), index=True, nullable=False)
    decision = Column(String(255), nullable=False)
    reasoning_inputs = Column(JSON, nullable=False)
    outcome = Column(String(128), nullable=True)
