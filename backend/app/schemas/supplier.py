from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class BusinessProfileUpdate(BaseModel):
    name: Optional[str] = None
    enterprise_type: Optional[str] = None  # micro, small, medium
    udyam_number: Optional[str] = None
    pan: Optional[str] = None
    gstin: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    industry_category: Optional[str] = None
    purchasing_interests: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class BusinessProfileResponse(BaseModel):
    id: int
    name: str
    enterprise_type: str
    udyam_number: str
    pan: Optional[str] = None
    gstin: Optional[str] = None
    state: str
    district: str
    industry_category: str
    purchasing_interests: str
    contact_email: str
    contact_phone: str
    created_at: datetime

    class Config:
        from_attributes = True


class SupplierListingResponse(BaseModel):
    id: int
    company_name: str
    industry_category: str
    product_tags: str
    contact_person: str
    contact_email: str
    contact_phone: str
    city: str
    state: str
    is_sponsored: bool
    sponsorship_tier: str
    verified: bool
    description: str
    min_order_quantity: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SupplierEnquiryCreate(BaseModel):
    supplier_id: int
    requester_company_name: str
    requester_name: str
    requester_email: str
    requester_phone: str
    product_interest: str
    message: str
    consent_given: bool = Field(..., description="User must explicitly consent to sharing contact details")


class SupplierEnquiryResponse(BaseModel):
    id: int
    supplier_id: int
    business_profile_id: Optional[int] = None
    requester_company_name: str
    requester_name: str
    requester_email: str
    requester_phone: str
    product_interest: str
    message: str
    consent_given: bool
    consent_timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True
