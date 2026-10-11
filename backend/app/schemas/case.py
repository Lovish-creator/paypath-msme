from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import date, datetime


class EvidenceItemBase(BaseModel):
    category: str  # invoice, purchase_order, delivery_proof, acceptance_record, buyer_comm, payment_receipt, udyam_certificate, other
    title: str
    status: str = "missing"  # provided, missing, not_applicable, needs_review
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    notes: Optional[str] = None


class EvidenceItemCreate(EvidenceItemBase):
    pass


class EvidenceItemUpdate(BaseModel):
    status: Optional[str] = None
    title: Optional[str] = None
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    notes: Optional[str] = None


class EvidenceItemResponse(EvidenceItemBase):
    id: int
    case_id: int
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FollowUpEventBase(BaseModel):
    event_type: str  # friendly_reminder, firm_follow_up, phone_call, formal_notice_drafted, formal_notice_served, payment_promised, evidence_reviewed, report_generated, samadhaan_application_prepared, custom
    summary: str
    detail: Optional[str] = None
    next_action_date: Optional[date] = None
    recorded_by: Optional[str] = "Finance Lead"


class FollowUpEventCreate(FollowUpEventBase):
    pass


class FollowUpEventResponse(FollowUpEventBase):
    id: int
    case_id: int
    performed_at: datetime

    class Config:
        from_attributes = True


class CaseStageUpdate(BaseModel):
    current_stage: int = Field(..., ge=1, le=8)
    notes: Optional[str] = None
    promised_payment_date: Optional[date] = None
    promised_payment_amount: Optional[float] = None


class InvoiceSummaryForCase(BaseModel):
    id: int
    invoice_number: str
    buyer_name: str
    buyer_gstin: Optional[str] = None
    buyer_contact_email: Optional[str] = None
    buyer_contact_phone: Optional[str] = None
    invoice_date: date
    delivery_date: Optional[date] = None
    acceptance_date: Optional[date] = None
    has_written_agreement: bool = True
    agreed_credit_days: Optional[int] = 30
    total_amount: float
    paid_amount: float
    outstanding_balance: float
    status: str
    goods_services_description: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class CaseDetailResponse(BaseModel):
    id: int
    invoice_id: int
    reference_code: str
    current_stage: int
    stage_label: str
    priority: str
    promised_payment_date: Optional[date] = None
    promised_payment_amount: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    invoice: Optional[InvoiceSummaryForCase] = None
    evidence_items: List[EvidenceItemResponse] = []
    follow_up_events: List[FollowUpEventResponse] = []
    timeline: Optional[Dict[str, Any]] = None
    completeness_summary: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ReminderDraftRequest(BaseModel):
    tone: str = "friendly"  # friendly, firm, formal_notice
    sender_name: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_designation: Optional[str] = "Accounts Payable / CFO"
    custom_message: Optional[str] = None


class ReminderDraftResponse(BaseModel):
    tone: str
    subject: str
    body_markdown: str
    notice_title: str
    has_statutory_citations: bool
    review_disclaimer: str
    created_at: datetime
