from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date


class DashboardMetricCard(BaseModel):
    label: str
    value: float | int | str
    formatted_value: str
    change_label: Optional[str] = None
    alert: bool = False


class ApproachingInvoice(BaseModel):
    invoice_id: int
    invoice_number: str
    buyer_name: str
    outstanding_balance: float
    due_date: str
    days_remaining: int


class PromisedPaymentAlert(BaseModel):
    case_id: int
    case_reference: str
    buyer_name: str
    promised_amount: float
    promised_date: str
    is_overdue: bool


class DashboardResponse(BaseModel):
    total_outstanding_amount: float
    total_overdue_amount: float
    total_invoices_count: int
    overdue_invoices_count: int
    approaching_due_count: int
    cases_awaiting_followup_count: int
    promised_payments_count: int
    
    formatted_total_outstanding: str
    formatted_total_overdue: str
    
    stage_breakdown: Dict[str, int]
    approaching_invoices: List[ApproachingInvoice]
    promised_payment_alerts: List[PromisedPaymentAlert]
    recent_followups: List[Dict[str, Any]]
