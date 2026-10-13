from fastapi import APIRouter, Depends, Query, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.db.database import get_db
from backend.app.core.auth import get_current_business
from backend.app.models.business import BusinessProfile
from backend.app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    PaymentCreate,
    PaymentResponse,
    InvoiceExtractionResult,
)
from backend.app.services.invoice_service import InvoiceService
from backend.app.services.document_extractor import DocumentExtractor

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("/extract-document", response_model=InvoiceExtractionResult)
async def extract_invoice_document(
    file: UploadFile = File(...),
    current_business: BusinessProfile = Depends(get_current_business),
):
    """
    Accepts an uploaded invoice PDF or image, saves it securely,
    extracts metadata and text, and returns verified field suggestions.
    """
    filename = file.filename or "invoice.pdf"
    content = await file.read()
    
    # Validation
    if len(content) > 15 * 1024 * 1024:  # 15MB limit
        raise HTTPException(status_code=400, detail="Invoice file size exceeds 15MB limit")
    
    unique_name, saved_path = DocumentExtractor.save_uploaded_file(filename, content)
    result = DocumentExtractor.extract_from_pdf(saved_path, filename)
    return result


@router.get("", response_model=List[InvoiceResponse])
def list_invoices(
    search: Optional[str] = Query(None, description="Search by invoice number, buyer name, or GSTIN"),
    status: Optional[str] = Query(None, description="Filter by status"),
    overdue_only: bool = Query(False, description="Filter strictly overdue invoices"),
    current_business: BusinessProfile = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return InvoiceService.get_invoices(
        db=db,
        business_profile_id=current_business.id,
        search=search,
        status=status,
        overdue_only=overdue_only,
    )


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: InvoiceCreate,
    current_business: BusinessProfile = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return InvoiceService.create_invoice(
        db=db,
        payload=payload,
        business_profile_id=current_business.id,
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    current_business: BusinessProfile = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return InvoiceService.get_invoice_by_id(
        db=db,
        invoice_id=invoice_id,
        business_profile_id=current_business.id,
    )


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    payload: InvoiceUpdate,
    current_business: BusinessProfile = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return InvoiceService.update_invoice(
        db=db,
        invoice_id=invoice_id,
        payload=payload,
        business_profile_id=current_business.id,
    )


@router.post("/{invoice_id}/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def record_payment(
    invoice_id: int,
    payload: PaymentCreate,
    current_business: BusinessProfile = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return InvoiceService.record_payment(
        db=db,
        invoice_id=invoice_id,
        payload=payload,
        business_profile_id=current_business.id,
    )

