from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import Dict, Any, List

from backend.app.models.invoice import Invoice
from backend.app.models.case import Case, FollowUpEvent
from backend.app.models.business import BusinessProfile
from backend.app.services.legal_engine import LegalEngine
from backend.app.schemas.dashboard import (
    DashboardResponse,
    ApproachingInvoice,
    PromisedPaymentAlert,
)


def format_inr(amount: float) -> str:
    """Format number as Indian Rupee (₹) format with comma separators"""
    try:
        s = f"{amount:,.2f}"
        return f"₹{s}"
    except Exception:
        return f"₹{amount}"


class DashboardService:
    @staticmethod
    def get_dashboard_metrics(db: Session, business_profile_id: int = 1) -> DashboardResponse:
        invoices = db.query(Invoice).filter(Invoice.business_profile_id == business_profile_id).all()
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == business_profile_id).first()
        enterprise_type = profile.enterprise_type if profile else "micro"
        udyam_registered = bool(profile.udyam_number) if profile else True

        total_outstanding = 0.0
        total_overdue = 0.0
        overdue_count = 0
        approaching_list: List[ApproachingInvoice] = []
        
        today = date.today()

        for inv in invoices:
            total_outstanding += inv.outstanding_balance
            
            if inv.outstanding_balance > 0:
                timeline = LegalEngine.calculate_timeline_and_interest(
                    invoice_date=inv.invoice_date,
                    delivery_date=inv.delivery_date,
                    acceptance_date=inv.acceptance_date,
                    has_objection=inv.has_objection,
                    objection_date=inv.objection_date,
                    objection_resolved_date=inv.objection_resolved_date,
                    has_written_agreement=inv.has_written_agreement,
                    agreed_credit_days=inv.agreed_credit_days,
                    outstanding_principal=inv.outstanding_balance,
                    enterprise_type=enterprise_type,
                    udyam_registered=udyam_registered,
                    as_of_date=today,
                )

                if timeline["is_overdue"]:
                    total_overdue += inv.outstanding_balance
                    overdue_count += 1
                elif 0 <= timeline["days_remaining"] <= 14:
                    approaching_list.append(
                        ApproachingInvoice(
                            invoice_id=inv.id,
                            invoice_number=inv.invoice_number,
                            buyer_name=inv.buyer_name,
                            outstanding_balance=inv.outstanding_balance,
                            due_date=timeline["calculated_due_date"],
                            days_remaining=timeline["days_remaining"],
                        )
                    )

        # Sort approaching invoices by days remaining ascending
        approaching_list.sort(key=lambda x: x.days_remaining)

        # Cases metrics
        cases = db.query(Case).join(Invoice).filter(Invoice.business_profile_id == business_profile_id).all()
        
        stage_breakdown = {
            "Stage 1: Recorded": 0,
            "Stage 2: Due Approaching": 0,
            "Stage 3: Friendly Reminder": 0,
            "Stage 4: Follow-up": 0,
            "Stage 5: Formal Notice": 0,
            "Stage 6: Evidence Audit": 0,
            "Stage 7: Report Ready": 0,
            "Stage 8: MSEFC Escalation": 0,
        }
        
        stage_keys = [
            "Stage 1: Recorded",
            "Stage 2: Due Approaching",
            "Stage 3: Friendly Reminder",
            "Stage 4: Follow-up",
            "Stage 5: Formal Notice",
            "Stage 6: Evidence Audit",
            "Stage 7: Report Ready",
            "Stage 8: MSEFC Escalation",
        ]

        promised_alerts: List[PromisedPaymentAlert] = []
        cases_awaiting_followup = 0

        for c in cases:
            if 1 <= c.current_stage <= 8:
                stage_breakdown[stage_keys[c.current_stage - 1]] += 1

            if c.promised_payment_date:
                is_p_overdue = c.promised_payment_date < today and (c.invoice.outstanding_balance > 0)
                promised_alerts.append(
                    PromisedPaymentAlert(
                        case_id=c.id,
                        case_reference=c.reference_code,
                        buyer_name=c.invoice.buyer_name,
                        promised_amount=c.promised_payment_amount or c.invoice.outstanding_balance,
                        promised_date=c.promised_payment_date.isoformat(),
                        is_overdue=is_p_overdue,
                    )
                )

            # Check if case awaits follow-up (unpaid invoice and no follow-up in last 7 days)
            if c.invoice.outstanding_balance > 0:
                recent_events = [ev for ev in c.follow_up_events if (datetime.utcnow() - ev.performed_at).days <= 7]
                if not recent_events:
                    cases_awaiting_followup += 1

        # Recent follow-up activity
        recent_events_query = (
            db.query(FollowUpEvent)
            .join(Case)
            .join(Invoice)
            .filter(Invoice.business_profile_id == business_profile_id)
            .order_by(FollowUpEvent.performed_at.desc())
            .limit(6)
            .all()
        )
        recent_followups = [
            {
                "id": ev.id,
                "case_reference": ev.case.reference_code,
                "buyer_name": ev.case.invoice.buyer_name,
                "event_type": ev.event_type,
                "summary": ev.summary,
                "performed_at": ev.performed_at.isoformat(),
                "recorded_by": ev.recorded_by,
            }
            for ev in recent_events_query
        ]

        total_outstanding = round(total_outstanding, 2)
        total_overdue = round(total_overdue, 2)

        return DashboardResponse(
            total_outstanding_amount=total_outstanding,
            total_overdue_amount=total_overdue,
            total_invoices_count=len(invoices),
            overdue_invoices_count=overdue_count,
            approaching_due_count=len(approaching_list),
            cases_awaiting_followup_count=cases_awaiting_followup,
            promised_payments_count=len(promised_alerts),
            formatted_total_outstanding=format_inr(total_outstanding),
            formatted_total_overdue=format_inr(total_overdue),
            stage_breakdown=stage_breakdown,
            approaching_invoices=approaching_list,
            promised_payment_alerts=promised_alerts,
            recent_followups=recent_followups,
        )
