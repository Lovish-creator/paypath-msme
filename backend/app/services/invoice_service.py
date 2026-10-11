from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from fastapi import HTTPException

from backend.app.models.invoice import Invoice, Payment
from backend.app.models.case import Case, EvidenceItem, FollowUpEvent
from backend.app.models.business import BusinessProfile
from backend.app.schemas.invoice import InvoiceCreate, InvoiceUpdate, PaymentCreate
from backend.app.services.legal_engine import LegalEngine


STAGE_LABELS = {
    1: "Invoice Recorded",
    2: "Payment Due Approaching",
    3: "Friendly Reminder Prepared",
    4: "Follow-up Recorded",
    5: "Formal Notice Draft Prepared",
    6: "Evidence Completeness Reviewed",
    7: "Case-Preparation Report Generated",
    8: "Samadhaan / MSEFC Filing Identified",
}


DEFAULT_EVIDENCE_TEMPLATES = [
    ("invoice", "Original Tax Invoice with GSTIN & HSN Details"),
    ("purchase_order", "Purchase Order (PO) / Written Commercial Agreement"),
    ("delivery_proof", "Proof of Delivery / Transporter LR / Delivery Challan"),
    ("acceptance_record", "Goods Acceptance / Inspection Memo (or Deemed Acceptance Record)"),
    ("buyer_comm", "Buyer Correspondence (WhatsApp, Email Acknowledgements, Follow-ups)"),
    ("payment_receipt", "Bank Account Statement / Partial Payment Records"),
    ("udyam_certificate", "Udyam Registration Certificate of Supplier Enterprise"),
]


class InvoiceService:
    @staticmethod
    def get_invoices(
        db: Session,
        business_profile_id: int = 1,
        search: Optional[str] = None,
        status: Optional[str] = None,
        overdue_only: bool = False,
    ) -> List[Invoice]:
        query = db.query(Invoice).filter(Invoice.business_profile_id == business_profile_id)
        
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Invoice.invoice_number.ilike(search_pattern),
                    Invoice.buyer_name.ilike(search_pattern),
                    Invoice.buyer_gstin.ilike(search_pattern),
                )
            )
            
        if status:
            query = query.filter(Invoice.status == status)
            
        invoices = query.order_by(Invoice.invoice_date.desc()).all()
        
        # Enrich and sync status if needed
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == business_profile_id).first()
        enterprise_type = profile.enterprise_type if profile else "micro"
        udyam_registered = bool(profile.udyam_number) if profile else True
        
        filtered = []
        for inv in invoices:
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
            )
            
            # Dynamic status update if unpaid and past due
            if inv.outstanding_balance > 0:
                if timeline["is_overdue"]:
                    if inv.status not in ("escalated", "overdue"):
                        inv.status = "overdue"
                else:
                    if inv.paid_amount > 0 and inv.status != "partially_paid":
                        inv.status = "partially_paid"
                    elif inv.status == "overdue":
                        inv.status = "issued"
            else:
                if inv.status != "paid":
                    inv.status = "paid"
            
            # If overdue_only filter is applied
            if overdue_only and not timeline["is_overdue"]:
                continue
                
            inv.timeline = timeline  # type: ignore
            filtered.append(inv)
            
        db.commit()
        return filtered

    @staticmethod
    def get_invoice_by_id(db: Session, invoice_id: int) -> Invoice:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
            
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == invoice.business_profile_id).first()
        enterprise_type = profile.enterprise_type if profile else "micro"
        udyam_registered = bool(profile.udyam_number) if profile else True

        timeline = LegalEngine.calculate_timeline_and_interest(
            invoice_date=invoice.invoice_date,
            delivery_date=invoice.delivery_date,
            acceptance_date=invoice.acceptance_date,
            has_objection=invoice.has_objection,
            objection_date=invoice.objection_date,
            objection_resolved_date=invoice.objection_resolved_date,
            has_written_agreement=invoice.has_written_agreement,
            agreed_credit_days=invoice.agreed_credit_days,
            outstanding_principal=invoice.outstanding_balance,
            enterprise_type=enterprise_type,
            udyam_registered=udyam_registered,
        )
        invoice.timeline = timeline  # type: ignore
        return invoice

    @staticmethod
    def create_invoice(db: Session, payload: InvoiceCreate, business_profile_id: int = 1) -> Invoice:
        # Check uniqueness of invoice_number
        existing = db.query(Invoice).filter(
            Invoice.invoice_number == payload.invoice_number,
            Invoice.business_profile_id == business_profile_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Invoice number '{payload.invoice_number}' already exists")

        total = round(payload.total_amount, 2)
        invoice = Invoice(
            invoice_number=payload.invoice_number.strip(),
            business_profile_id=business_profile_id,
            buyer_name=payload.buyer_name.strip(),
            buyer_gstin=payload.buyer_gstin.strip() if payload.buyer_gstin else None,
            buyer_contact_email=payload.buyer_contact_email.strip() if payload.buyer_contact_email else None,
            buyer_contact_phone=payload.buyer_contact_phone.strip() if payload.buyer_contact_phone else None,
            invoice_date=payload.invoice_date,
            delivery_date=payload.delivery_date,
            acceptance_date=payload.acceptance_date,
            has_objection=payload.has_objection,
            objection_date=payload.objection_date,
            objection_resolved_date=payload.objection_resolved_date,
            has_written_agreement=payload.has_written_agreement,
            agreed_credit_days=payload.agreed_credit_days,
            total_amount=total,
            paid_amount=0.0,
            outstanding_balance=total,
            status="issued",
            goods_services_description=payload.goods_services_description,
            notes=payload.notes,
        )
        db.add(invoice)
        db.flush()

        # Initialize corresponding Case
        ref_code = f"CASE-{invoice.invoice_number}"
        case = Case(
            invoice_id=invoice.id,
            reference_code=ref_code,
            current_stage=1,
            stage_label=STAGE_LABELS[1],
            priority="medium",
            notes="Case auto-initiated upon invoice recording.",
        )
        db.add(case)
        db.flush()

        # Initialize Default Evidence Checklist Items
        for category, title in DEFAULT_EVIDENCE_TEMPLATES:
            ev = EvidenceItem(
                case_id=case.id,
                category=category,
                title=title,
                status="missing",
            )
            db.add(ev)

        # Log Initial Follow-up Event
        follow_up = FollowUpEvent(
            case_id=case.id,
            event_type="invoice_created",
            summary=f"Invoice {invoice.invoice_number} recorded in PayPath",
            detail=f"Issued to {invoice.buyer_name} for total amount ₹{invoice.total_amount:,.2f}.",
            recorded_by="System",
        )
        db.add(follow_up)

        db.commit()
        db.refresh(invoice)
        return InvoiceService.get_invoice_by_id(db, invoice.id)

    @staticmethod
    def update_invoice(db: Session, invoice_id: int, payload: InvoiceUpdate) -> Invoice:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        update_data = payload.dict(exclude_unset=True)
        if "total_amount" in update_data and update_data["total_amount"] is not None:
            new_total = round(update_data["total_amount"], 2)
            if new_total < invoice.paid_amount:
                raise HTTPException(
                    status_code=400,
                    detail=f"Total amount cannot be less than already paid amount (₹{invoice.paid_amount:,.2f})"
                )
            invoice.total_amount = new_total
            invoice.outstanding_balance = round(new_total - invoice.paid_amount, 2)

        for key, val in update_data.items():
            if key != "total_amount":
                setattr(invoice, key, val)

        # Sync status
        if invoice.outstanding_balance == 0:
            invoice.status = "paid"
        elif invoice.paid_amount > 0:
            invoice.status = "partially_paid"

        db.commit()
        db.refresh(invoice)
        return InvoiceService.get_invoice_by_id(db, invoice.id)

    @staticmethod
    def record_payment(db: Session, invoice_id: int, payload: PaymentCreate) -> Payment:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        pay_amount = round(payload.amount, 2)
        if pay_amount <= 0:
            raise HTTPException(status_code=400, detail="Payment amount must be greater than zero")

        if pay_amount > invoice.outstanding_balance:
            raise HTTPException(
                status_code=400,
                detail=f"Payment amount (₹{pay_amount:,.2f}) exceeds outstanding balance (₹{invoice.outstanding_balance:,.2f})"
            )

        payment = Payment(
            invoice_id=invoice.id,
            payment_date=payload.payment_date,
            amount=pay_amount,
            reference_number=payload.reference_number.strip() if payload.reference_number else None,
            payment_mode=payload.payment_mode,
            notes=payload.notes,
        )
        db.add(payment)

        # Update invoice balances
        invoice.paid_amount = round(invoice.paid_amount + pay_amount, 2)
        invoice.outstanding_balance = round(invoice.total_amount - invoice.paid_amount, 2)

        if invoice.outstanding_balance == 0:
            invoice.status = "paid"
        else:
            invoice.status = "partially_paid"

        # Log event on Case
        case = db.query(Case).filter(Case.invoice_id == invoice.id).first()
        if case:
            event = FollowUpEvent(
                case_id=case.id,
                event_type="payment_recorded",
                summary=f"Payment of ₹{pay_amount:,.2f} recorded",
                detail=f"Ref: {payload.reference_number or 'N/A'}. New outstanding balance: ₹{invoice.outstanding_balance:,.2f}.",
                recorded_by="Finance Team",
            )
            db.add(event)

            # Auto-mark payment receipt evidence item as provided if exists
            receipt_item = db.query(EvidenceItem).filter(
                EvidenceItem.case_id == case.id,
                EvidenceItem.category == "payment_receipt"
            ).first()
            if receipt_item:
                receipt_item.status = "provided"
                receipt_item.notes = f"Payment ref {payload.reference_number} verified"

        db.commit()
        db.refresh(payment)
        return payment
