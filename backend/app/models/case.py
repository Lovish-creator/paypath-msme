from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.db.database import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), unique=True, nullable=False)
    reference_code = Column(String(50), unique=True, index=True, nullable=False)
    
    current_stage = Column(Integer, nullable=False, default=1)  # 1 to 8
    stage_label = Column(String(100), nullable=False, default="Invoice Recorded")
    priority = Column(String(50), nullable=False, default="medium")  # low, medium, high, critical
    
    promised_payment_date = Column(Date, nullable=True)
    promised_payment_amount = Column(Float, nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="case")
    evidence_items = relationship("EvidenceItem", back_populates="case", cascade="all, delete-orphan", order_by="EvidenceItem.id.asc()")
    follow_up_events = relationship("FollowUpEvent", back_populates="case", cascade="all, delete-orphan", order_by="FollowUpEvent.performed_at.desc()")


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    category = Column(String(50), nullable=False)  # invoice, purchase_order, delivery_proof, acceptance_record, buyer_comm, payment_receipt, udyam_certificate, other
    title = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="missing")  # provided, missing, not_applicable, needs_review
    file_name = Column(String(255), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    case = relationship("Case", back_populates="evidence_items")


class FollowUpEvent(Base):
    __tablename__ = "follow_up_events"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    event_type = Column(String(100), nullable=False)  # friendly_reminder, firm_follow_up, phone_call, formal_notice_drafted, formal_notice_served, payment_promised, evidence_reviewed, report_generated, samadhaan_application_prepared, custom
    performed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    summary = Column(String(255), nullable=False)
    detail = Column(Text, nullable=True)
    next_action_date = Column(Date, nullable=True)
    recorded_by = Column(String(100), nullable=False, default="MSME Finance Lead")

    case = relationship("Case", back_populates="follow_up_events")
