from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException

from backend.app.models.supplier import SupplierListing, SupplierEnquiry
from backend.app.models.business import BusinessProfile
from backend.app.schemas.supplier import SupplierEnquiryCreate, BusinessProfileUpdate


class SupplierService:
    @staticmethod
    def get_matched_suppliers(
        db: Session,
        business_profile_id: int = 1,
        category: Optional[str] = None,
        query_text: Optional[str] = None,
    ) -> List[SupplierListing]:
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == business_profile_id).first()
        
        target_category = category or (profile.industry_category if profile else None)
        interests = [i.strip().lower() for i in profile.purchasing_interests.split(",")] if (profile and profile.purchasing_interests) else []

        suppliers = db.query(SupplierListing).all()
        
        scored_suppliers = []
        for s in suppliers:
            score = 0
            # Explicit category match
            if target_category and s.industry_category.lower() == target_category.lower():
                score += 10
            
            # Product tags matching business purchasing interests
            tags = [t.strip().lower() for t in s.product_tags.split(",")]
            for tag in tags:
                for interest in interests:
                    if interest in tag or tag in interest:
                        score += 5
            
            # Text search filter
            if query_text:
                q = query_text.lower()
                if q in s.company_name.lower() or q in s.description.lower() or q in s.product_tags.lower():
                    score += 20
                else:
                    score = -1  # filter out if doesn't match query

            if s.is_sponsored:
                score += 2  # slight sponsored boost in ranking, but fully labelled!

            if score >= 0:
                scored_suppliers.append((score, s))

        # Sort by score desc, then company name
        scored_suppliers.sort(key=lambda x: (x[0], x[1].company_name), reverse=True)
        return [item[1] for item in scored_suppliers]

    @staticmethod
    def get_supplier_by_id(db: Session, supplier_id: int) -> SupplierListing:
        supplier = db.query(SupplierListing).filter(SupplierListing.id == supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier listing not found")
        return supplier

    @staticmethod
    def submit_enquiry(db: Session, payload: SupplierEnquiryCreate, business_profile_id: Optional[int] = 1) -> SupplierEnquiry:
        # Validate consent requirement
        if not payload.consent_given:
            raise HTTPException(
                status_code=400,
                detail="Explicit user consent is mandatory to forward contact details to the supplier."
            )

        supplier = db.query(SupplierListing).filter(SupplierListing.id == payload.supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier listing not found")

        enquiry = SupplierEnquiry(
            supplier_id=supplier.id,
            business_profile_id=business_profile_id,
            requester_company_name=payload.requester_company_name.strip(),
            requester_name=payload.requester_name.strip(),
            requester_email=payload.requester_email.strip(),
            requester_phone=payload.requester_phone.strip(),
            product_interest=payload.product_interest.strip(),
            message=payload.message.strip(),
            consent_given=True,
            consent_timestamp=datetime.now(timezone.utc),
        )
        db.add(enquiry)
        db.commit()
        db.refresh(enquiry)
        return enquiry

    @staticmethod
    def get_enquiries_for_business(db: Session, business_profile_id: int = 1) -> List[SupplierEnquiry]:
        return db.query(SupplierEnquiry).filter(
            SupplierEnquiry.business_profile_id == business_profile_id
        ).order_by(SupplierEnquiry.created_at.desc()).all()

    @staticmethod
    def get_enquiries_for_supplier(db: Session, supplier_id: int) -> List[SupplierEnquiry]:
        """Advertiser perspective: View enquiries received by supplier"""
        return db.query(SupplierEnquiry).filter(
            SupplierEnquiry.supplier_id == supplier_id
        ).order_by(SupplierEnquiry.created_at.desc()).all()

    @staticmethod
    def update_business_profile(db: Session, profile_id: int, payload: BusinessProfileUpdate) -> BusinessProfile:
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Business profile not found")

        for key, val in payload.model_dump(exclude_unset=True).items():
            setattr(profile, key, val)

        db.commit()
        db.refresh(profile)
        return profile

