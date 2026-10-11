from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from fastapi import HTTPException

from backend.app.models.case import Case, EvidenceItem, FollowUpEvent
from backend.app.models.invoice import Invoice
from backend.app.models.business import BusinessProfile
from backend.app.schemas.case import (
    CaseStageUpdate,
    EvidenceItemCreate,
    EvidenceItemUpdate,
    FollowUpEventCreate,
    ReminderDraftRequest,
    ReminderDraftResponse,
)
from backend.app.services.legal_engine import LegalEngine
from backend.app.services.invoice_service import STAGE_LABELS


class CaseService:
    @staticmethod
    def get_case(db: Session, case_id: int) -> Case:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        return CaseService._enrich_case(db, case)

    @staticmethod
    def get_case_by_invoice_id(db: Session, invoice_id: int) -> Case:
        case = db.query(Case).filter(Case.invoice_id == invoice_id).first()
        if not case:
            raise HTTPException(status_code=404, detail=f"Case for invoice id {invoice_id} not found")
        return CaseService._enrich_case(db, case)

    @staticmethod
    def _enrich_case(db: Session, case: Case) -> Case:
        invoice = case.invoice
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
        case.timeline = timeline  # type: ignore

        # Completeness summary
        items = case.evidence_items
        total_items = len(items)
        provided_count = sum(1 for it in items if it.status == "provided")
        missing_count = sum(1 for it in items if it.status == "missing")
        needs_review_count = sum(1 for it in items if it.status == "needs_review")
        na_count = sum(1 for it in items if it.status == "not_applicable")

        completeness_pct = round((provided_count / total_items * 100), 1) if total_items > 0 else 0.0

        case.completeness_summary = {  # type: ignore
            "total_items": total_items,
            "provided_count": provided_count,
            "missing_count": missing_count,
            "needs_review_count": needs_review_count,
            "not_applicable_count": na_count,
            "completeness_percentage": completeness_pct,
            "is_fileable": provided_count >= 4 and missing_count == 0,
        }
        return case

    @staticmethod
    def update_case_stage(db: Session, case_id: int, payload: CaseStageUpdate) -> Case:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        old_stage = case.current_stage
        case.current_stage = payload.current_stage
        case.stage_label = STAGE_LABELS.get(payload.current_stage, f"Stage {payload.current_stage}")

        if payload.promised_payment_date:
            case.promised_payment_date = payload.promised_payment_date
        if payload.promised_payment_amount is not None:
            case.promised_payment_amount = payload.promised_payment_amount
        if payload.notes:
            case.notes = payload.notes

        # Log transition event
        event = FollowUpEvent(
            case_id=case.id,
            event_type="stage_advanced",
            summary=f"Escalation Stage updated: {case.stage_label} (Stage {case.current_stage})",
            detail=f"Previous Stage: {STAGE_LABELS.get(old_stage, old_stage)}. Notes: {payload.notes or 'None'}",
            next_action_date=payload.promised_payment_date,
            recorded_by="Operations Lead",
        )
        db.add(event)

        db.commit()
        db.refresh(case)
        return CaseService.get_case(db, case.id)

    @staticmethod
    def update_evidence_item(db: Session, case_id: int, item_id: int, payload: EvidenceItemUpdate) -> EvidenceItem:
        item = db.query(EvidenceItem).filter(
            EvidenceItem.id == item_id,
            EvidenceItem.case_id == case_id
        ).first()
        if not item:
            raise HTTPException(status_code=404, detail="Evidence item not found")

        update_data = payload.dict(exclude_unset=True)
        for key, val in update_data.items():
            setattr(item, key, val)

        if "status" in update_data and update_data["status"] == "provided" and not item.uploaded_at:
            item.uploaded_at = datetime.utcnow()

        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def add_follow_up_event(db: Session, case_id: int, payload: FollowUpEventCreate) -> FollowUpEvent:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        event = FollowUpEvent(
            case_id=case.id,
            event_type=payload.event_type,
            summary=payload.summary.strip(),
            detail=payload.detail,
            next_action_date=payload.next_action_date,
            recorded_by=payload.recorded_by or "Finance Lead",
        )
        db.add(event)

        # If event is payment_promised, sync with case
        if payload.event_type == "payment_promised" and payload.next_action_date:
            case.promised_payment_date = payload.next_action_date

        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def generate_reminder_draft(db: Session, case_id: int, req: ReminderDraftRequest) -> ReminderDraftResponse:
        case = CaseService.get_case(db, case_id)
        invoice = case.invoice
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == invoice.business_profile_id).first()
        
        supplier_name = profile.name if profile else "Our Enterprise"
        supplier_udyam = profile.udyam_number if profile else "UDYAM Registered"
        supplier_contact = profile.contact_phone if profile else "+91 98765 43210"
        recipient = req.recipient_name or invoice.buyer_name
        designation = req.recipient_designation or "Accounts Payable / Senior Management"
        custom = req.custom_message or ""

        timeline = case.timeline  # type: ignore
        due_date_str = timeline.get("calculated_due_date", str(invoice.invoice_date))
        days_overdue = timeline.get("days_overdue", 0)
        principal = invoice.outstanding_balance
        interest = timeline.get("estimated_interest", 0.0)
        total_claimable = timeline.get("total_claimable_amount", principal)
        annual_rate = timeline.get("annual_statutory_interest_rate_pct", 20.25)

        disclaimer = (
            "DRAFT FOR BUSINESS COMMUNICATION ONLY — This draft communication is prepared by PayPath MSME "
            "as an administrative and factual organizational aid. It does not constitute formal legal advice or a certified "
            "legal notice unless reviewed and dispatched by an authorized legal practitioner."
        )

        if req.tone == "friendly":
            notice_title = "Friendly Payment Reminder"
            subject = f"Friendly Reminder: Outstanding Payment for Invoice #{invoice.invoice_number} — {supplier_name}"
            body = f"""Dear {recipient},
Attention: {designation}

Greetings from {supplier_name}.

We hope this email finds you well. We are writing to bring to your kind attention that payment for Invoice #{invoice.invoice_number}, dated {invoice.invoice_date}, for an outstanding amount of ₹{principal:,.2f}, was due on {due_date_str}.

**Invoice Summary:**
- **Invoice Number**: {invoice.invoice_number}
- **Invoice Date**: {invoice.invoice_date}
- **Due Date**: {due_date_str}
- **Total Amount**: ₹{invoice.total_amount:,.2f}
- **Amount Received**: ₹{invoice.paid_amount:,.2f}
- **Outstanding Balance**: ₹{principal:,.2f}

{f"**Additional Note:** {custom}" if custom else ""}

We value our commercial partnership and understand that delays occasionally happen due to routine processing cycles. Could you kindly verify this with your accounts department and share the expected date of settlement or UTR reference?

Please find our banking details for reference:
- Beneficiary Name: {supplier_name}
- MSME Registration: {supplier_udyam}

Thank you for your prompt cooperation.

Warm regards,
{req.sender_name or "Finance Team"}
{supplier_name}
Phone: {supplier_contact}
"""
            has_citations = False

        elif req.tone == "firm":
            notice_title = "Urgent Payment Follow-Up Notice"
            subject = f"URGENT: Overdue Payment Notice ({days_overdue} Days Overdue) — Invoice #{invoice.invoice_number}"
            body = f"""Dear {recipient},
Attention: {designation}

Subject: URGENT DEMAND FOR PAYMENT — INVOICE #{invoice.invoice_number} (OVERDUE BY {days_overdue} DAYS)

We are writing with reference to our earlier correspondence regarding Invoice #{invoice.invoice_number} dated {invoice.invoice_date}, issued against delivery of goods/services.

Despite repeated follow-ups, an amount of **₹{principal:,.2f}** remains unpaid as of today.

**Key Transaction Facts:**
1. **Invoice Number**: {invoice.invoice_number}
2. **Invoice Date**: {invoice.invoice_date}
3. **Statutory Due Date**: {due_date_str}
4. **Days Overdue**: {days_overdue} days
5. **Outstanding Principal**: ₹{principal:,.2f}

**Statutory Compliance Notice:**
Please be apprised that {supplier_name} is a duly registered enterprise under the Micro, Small and Medium Enterprises Development (MSMED) Act, 2006 (Udyam Reg: {supplier_udyam}).

Under **Section 15 of the MSMED Act, 2006**, payments for goods and services delivered by a registered MSME must be cleared within the agreed period (not exceeding 45 days) or within 15 days of acceptance. Furthermore, under **Section 43B(h) of the Income Tax Act, 1961**, delay in clearing dues to Micro/Small enterprises results in disallowance of expenditure for income tax deductions.

{f"**Specific Context:** {custom}" if custom else ""}

We request you to remit the outstanding sum of **₹{principal:,.2f}** within 5 business days to avoid the accrual of statutory compound interest under Section 16 of the MSMED Act.

Sincerely,
{req.sender_name or "Finance & Accounts Department"}
{supplier_name}
"""
            has_citations = True

        else:  # formal_notice
            notice_title = "Formal Demand Notice under Section 15 & 16 of MSMED Act, 2006"
            subject = f"FORMAL DEMAND NOTICE: Dues for Invoice #{invoice.invoice_number} under Sections 15 & 16, MSMED Act, 2006"
            body = f"""**FORMAL PRE-LITIGATION DEMAND NOTICE**
*(Issued under Sections 15 & 16 of the Micro, Small and Medium Enterprises Development Act, 2006)*

**DRAFT FOR REVIEW**

To:
**{invoice.buyer_name}**
Attention: {designation}
GSTIN: {invoice.buyer_gstin or "As per records"}
Email: {invoice.buyer_contact_email or "accounts@buyer.com"}

From:
**{supplier_name}**
Udyam Registration No.: {supplier_udyam}
Contact: {supplier_contact}

Date: {date.today().strftime('%d %B %Y')}

**SUBJECT: FORMAL DEMAND FOR PAYMENT OF OUTSTANDING PRINCIPAL ₹{principal:,.2f} TOGETHER WITH STATUTORY COMPOUND INTEREST UNDER SECTION 16 OF THE MSMED ACT, 2006 (INVOICE #{invoice.invoice_number})**

Sir/Madam,

Under instructions and on behalf of our enterprise, **{supplier_name}**, we hereby place on record the following facts:

1. **Enterprise Status**: Our enterprise is a registered supplier enterprise under the Micro, Small and Medium Enterprises Development Act, 2006, holding Udyam Registration No. **{supplier_udyam}**.

2. **Supply & Acceptance**: Pursuant to commercial orders placed by you, our enterprise duly delivered the contracted goods/services under Invoice No. **{invoice.invoice_number}** dated **{invoice.invoice_date}** for a total sum of **₹{invoice.total_amount:,.2f}**. The goods were accepted without any written dispute within the statutory 15-day period under Section 2(b) of the MSMED Act.

3. **Default in Payment**: Under Section 15 of the MSMED Act, 2006, the statutory due date for payment was **{due_date_str}**. Despite our repeated requests and acknowledgements, you have failed to discharge your liability. As of date, the principal sum of **₹{principal:,.2f}** remains unpaid and is overdue by **{days_overdue} days**.

4. **Liability for Statutory Compound Interest (Section 16)**:
   Section 16 of the MSMED Act, 2006 provides:
   > *"Where any buyer fails to make payment of the amount to the supplier as required under section 15, the buyer shall, notwithstanding anything contained in any agreement between the buyer and the supplier or in any law for the time being in force, be liable to pay compound interest with monthly rests to the supplier on that amount from the appointed day or, as the case may be, from the date immediately following the date agreed upon, at three times of the bank rate notified by the Reserve Bank."*

   Accordingly, compound interest computed at **{annual_rate}% p.a.** (3x current RBI Bank Rate) with monthly rests on the overdue principal amounts to **₹{interest:,.2f}**, bringing the total claimable sum to **₹{total_claimable:,.2f}**.

5. **Tax Disallowance under Section 43B(h)**:
   Kindly note that pursuant to Section 43B(h) of the Income Tax Act, 1961, any outstanding amount due to our enterprise beyond statutory MSMED timelines will be disallowed as a deductible expense in your computation of taxable income for the relevant financial year.

{f"**Additional Instructions:** {custom}" if custom else ""}

**FINAL DEMAND:**
You are hereby called upon to pay the total outstanding sum of **₹{total_claimable:,.2f}** (Principal: ₹{principal:,.2f} + Accrued Statutory Interest: ₹{interest:,.2f}) within **15 (fifteen) days** of receipt of this notice, failing which our enterprise shall be constrained to initiate formal conciliation and arbitration proceedings before the **Micro and Small Enterprises Facilitation Council (MSEFC)** under **Section 18 of the MSMED Act, 2006** and the **MSME Samadhaan Portal**, at your sole cost and legal consequence.

Yours faithfully,

For **{supplier_name}**
Authorized Signatory / Finance Lead
"""
            has_citations = True

        return ReminderDraftResponse(
            tone=req.tone,
            subject=subject,
            body_markdown=body,
            notice_title=notice_title,
            has_statutory_citations=has_citations,
            review_disclaimer=disclaimer,
            created_at=datetime.utcnow(),
        )
