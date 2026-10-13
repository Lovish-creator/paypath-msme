from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.db.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(100), unique=True, index=True, nullable=False)
    business_profile_id = Column(Integer, ForeignKey("business_profiles.id"), nullable=False, default=1)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=True)
    buyer_name = Column(String(255), nullable=False)
    buyer_gstin = Column(String(50), nullable=True)
    buyer_contact_email = Column(String(255), nullable=True)
    buyer_contact_phone = Column(String(50), nullable=True)

    invoice_date = Column(Date, nullable=False)
    delivery_date = Column(Date, nullable=True)
    acceptance_date = Column(Date, nullable=True)
    has_objection = Column(Boolean, default=False)
    objection_date = Column(Date, nullable=True)
    objection_resolved_date = Column(Date, nullable=True)

    has_written_agreement = Column(Boolean, default=True)
    agreed_credit_days = Column(Integer, nullable=True, default=30)

    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, nullable=False, default=0.0)
    outstanding_balance = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="issued")  # draft, issued, partially_paid, paid, overdue, escalated

    goods_services_description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    source_file_path = Column(String(500), nullable=True)
    extraction_metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    business_profile = relationship("BusinessProfile", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan", order_by="Payment.payment_date.desc()")
    case = relationship("Case", back_populates="invoice", uselist=False, cascade="all, delete-orphan")



class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    reference_number = Column(String(100), nullable=True)
    payment_mode = Column(String(50), nullable=True, default="Bank Transfer (NEFT/RTGS)")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="payments")
