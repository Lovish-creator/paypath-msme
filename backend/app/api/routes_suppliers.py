from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.db.database import get_db
from backend.app.models.business import BusinessProfile
from backend.app.schemas.supplier import (
    SupplierListingResponse,
    SupplierEnquiryCreate,
    SupplierEnquiryResponse,
    BusinessProfileResponse,
    BusinessProfileUpdate,
)
from backend.app.services.supplier_service import SupplierService

router = APIRouter(prefix="/suppliers", tags=["B2B Supplier Discovery"])


@router.get("", response_model=List[SupplierListingResponse])
def get_suppliers(
    category: Optional[str] = Query(None, description="Filter by industry category"),
    search: Optional[str] = Query(None, description="Search products or supplier name"),
    db: Session = Depends(get_db),
):
    return SupplierService.get_matched_suppliers(
        db=db,
        business_profile_id=1,
        category=category,
        query_text=search,
    )


@router.get("/profile/current", response_model=BusinessProfileResponse)
def get_current_business_profile(db: Session = Depends(get_db)):
    profile = db.query(BusinessProfile).filter(BusinessProfile.id == 1).first()
    return profile


@router.put("/profile/current", response_model=BusinessProfileResponse)
def update_current_business_profile(payload: BusinessProfileUpdate, db: Session = Depends(get_db)):
    return SupplierService.update_business_profile(db=db, profile_id=1, payload=payload)


@router.get("/enquiries/history", response_model=List[SupplierEnquiryResponse])
def get_enquiry_history(db: Session = Depends(get_db)):
    return SupplierService.get_enquiries_for_business(db=db, business_profile_id=1)


@router.get("/{supplier_id}", response_model=SupplierListingResponse)
def get_supplier_detail(supplier_id: int, db: Session = Depends(get_db)):
    return SupplierService.get_supplier_by_id(db=db, supplier_id=supplier_id)


@router.post("/{supplier_id}/enquiries", response_model=SupplierEnquiryResponse, status_code=status.HTTP_201_CREATED)
def submit_supplier_enquiry(
    supplier_id: int, payload: SupplierEnquiryCreate, db: Session = Depends(get_db)
):
    # Ensure URL id matches payload
    payload.supplier_id = supplier_id
    return SupplierService.submit_enquiry(db=db, payload=payload, business_profile_id=1)


@router.get("/{supplier_id}/advertiser-leads", response_model=List[SupplierEnquiryResponse])
def get_advertiser_leads(supplier_id: int, db: Session = Depends(get_db)):
    """Advertiser Perspective: View leads received for this supplier placement"""
    return SupplierService.get_enquiries_for_supplier(db=db, supplier_id=supplier_id)
