from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Dict
from datetime import date, datetime


class PaymentBase(BaseModel):
    payment_date: date
    amount: float = Field(..., gt=0, description="Payment amount must be greater than zero")
    reference_number: Optional[str] = None
    payment_mode: Optional[str] = "Bank Transfer (NEFT/RTGS)"
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int
    invoice_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    invoice_number: str
    buyer_name: str
    buyer_gstin: Optional[str] = None
    buyer_contact_email: Optional[str] = None
    buyer_contact_phone: Optional[str] = None
    
    invoice_date: date
    delivery_date: Optional[date] = None
    acceptance_date: Optional[date] = None
    
    has_objection: bool = False
    objection_date: Optional[date] = None
    objection_resolved_date: Optional[date] = None
    
    has_written_agreement: bool = False
    agreed_credit_days: Optional[int] = Field(default=None, ge=0, le=180)
    
    total_amount: float = Field(..., gt=0, description="Total invoice amount must be positive")
    goods_services_description: Optional[str] = None
    notes: Optional[str] = None
    source_file_path: Optional[str] = None
    extraction_metadata: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceExtractionResult(BaseModel):
    invoice_number: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_gstin: Optional[str] = None
    invoice_date: Optional[str] = None
    total_amount: Optional[float] = None
    agreed_credit_days: Optional[int] = None
    has_written_agreement: Optional[bool] = None
    confidence_score: float = 0.0
    raw_text_preview: str = ""
    source_file_name: str = ""
    saved_file_path: str = ""



class InvoiceUpdate(BaseModel):
    buyer_name: Optional[str] = None
    buyer_gstin: Optional[str] = None
    buyer_contact_email: Optional[str] = None
    buyer_contact_phone: Optional[str] = None
    
    invoice_date: Optional[date] = None
    delivery_date: Optional[date] = None
    acceptance_date: Optional[date] = None
    
    has_objection: Optional[bool] = None
    objection_date: Optional[date] = None
    objection_resolved_date: Optional[date] = None
    
    has_written_agreement: Optional[bool] = None
    agreed_credit_days: Optional[int] = None
    
    total_amount: Optional[float] = None
    goods_services_description: Optional[str] = None
    notes: Optional[str] = None


class CaseSummary(BaseModel):
    id: int
    reference_code: str
    current_stage: int
    stage_label: str
    priority: str
    promised_payment_date: Optional[date] = None
    promised_payment_amount: Optional[float] = None

    class Config:
        from_attributes = True


class InvoiceResponse(InvoiceBase):
    id: int
    business_profile_id: int
    buyer_id: Optional[int] = None
    paid_amount: float
    outstanding_balance: float
    status: str
    created_at: datetime
    updated_at: datetime
    payments: List[PaymentResponse] = []
    case: Optional[CaseSummary] = None
    timeline: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
