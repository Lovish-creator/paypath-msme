from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.core.auth import get_current_business
from backend.app.models.business import BusinessProfile
from backend.app.schemas.case import (
    CaseDetailResponse,
    CaseStageUpdate,
    EvidenceItemUpdate,
    EvidenceItemResponse,
    FollowUpEventCreate,
    FollowUpEventResponse,
    ReminderDraftRequest,
    ReminderDraftResponse,
)
from backend.app.services.case_service import CaseService
from backend.app.services.pdf_service import PDFService

router = APIRouter(prefix="/cases", tags=["Cases & Escalation"])


@router.get("/{case_id}", response_model=CaseDetailResponse)
def get_case_details(
    case_id: int,
    current_business: BusinessProfile = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return CaseService.get_case(db=db, case_id=case_id, business_profile_id=current_business.id)


@router.get("/by-invoice/{invoice_id}", response_model=CaseDetailResponse)
def get_case_by_invoice(
    invoice_id: int,
    current_business: BusinessProfile = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return CaseService.get_case_by_invoice_id(
        db=db,
        invoice_id=invoice_id,
        business_profile_id=current_business.id,
    )


@router.put("/{case_id}/stage", response_model=CaseDetailResponse)
def update_case_stage(
    case_id: int,
    payload: CaseStageUpdate,
    current_business: BusinessProfile = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return CaseService.update_case_stage(
        db=db,
        case_id=case_id,
        payload=payload,
        business_profile_id=current_business.id,
    )


@router.put("/{case_id}/evidence/{item_id}", response_model=EvidenceItemResponse)
def update_evidence_item(
    case_id: int,
    item_id: int,
    payload: EvidenceItemUpdate,
    current_business: BusinessProfile = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return CaseService.update_evidence_item(
        db=db,
        case_id=case_id,
        item_id=item_id,
        payload=payload,
        business_profile_id=current_business.id,
    )


@router.post("/{case_id}/events", response_model=FollowUpEventResponse, status_code=status.HTTP_201_CREATED)
def add_follow_up_event(
    case_id: int,
    payload: FollowUpEventCreate,
    current_business: BusinessProfile = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return CaseService.add_follow_up_event(
        db=db,
        case_id=case_id,
        payload=payload,
        business_profile_id=current_business.id,
    )


@router.post("/{case_id}/reminders", response_model=ReminderDraftResponse)
def generate_reminder_draft(
    case_id: int,
    payload: ReminderDraftRequest,
    current_business: BusinessProfile = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return CaseService.generate_reminder_draft(
        db=db,
        case_id=case_id,
        req=payload,
        business_profile_id=current_business.id,
    )


@router.get("/{case_id}/report/pdf")
def download_case_preparation_report(
    case_id: int,
    current_business: BusinessProfile = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    case = CaseService.get_case(db=db, case_id=case_id, business_profile_id=current_business.id)
    pdf_buffer = PDFService.generate_case_preparation_report(case, current_business)
    filename = f"PayPath_Case_Report_{case.reference_code}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

