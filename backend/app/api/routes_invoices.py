from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.db.database import get_db
from backend.app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    PaymentCreate,
    PaymentResponse,
)
from backend.app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("", response_model=List[InvoiceResponse])
def list_invoices(
    search: Optional[str] = Query(None, description="Search by invoice number, buyer name, or GSTIN"),
    status: Optional[str] = Query(None, description="Filter by status"),
    overdue_only: bool = Query(False, description="Filter strictly overdue invoices"),
    db: Session = Depends(get_db),
):
    return InvoiceService.get_invoices(
        db=db,
        business_profile_id=1,
        search=search,
        status=status,
        overdue_only=overdue_only,
    )


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    return InvoiceService.create_invoice(db=db, payload=payload, business_profile_id=1)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    return InvoiceService.get_invoice_by_id(db=db, invoice_id=invoice_id)


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(invoice_id: int, payload: InvoiceUpdate, db: Session = Depends(get_db)):
    return InvoiceService.update_invoice(db=db, invoice_id=invoice_id, payload=payload)


@router.post("/{invoice_id}/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def record_payment(invoice_id: int, payload: PaymentCreate, db: Session = Depends(get_db)):
    return InvoiceService.record_payment(db=db, invoice_id=invoice_id, payload=payload)
