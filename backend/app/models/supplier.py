from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime
from backend.app.db.database import Base


class SupplierListing(Base):
    __tablename__ = "supplier_listings"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    industry_category = Column(String(100), nullable=False)  # garment_manufacturing, packaging, industrial_components, business_services
    product_tags = Column(String(500), nullable=False)  # comma separated e.g. "polyester thread, industrial sewing needles, fabric buttons"
    contact_person = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    is_sponsored = Column(Boolean, default=True, nullable=False)
    sponsorship_tier = Column(String(50), default="featured", nullable=False)  # featured, sponsored, standard
    verified = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=False)
    min_order_quantity = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SupplierEnquiry(Base):
    __tablename__ = "supplier_enquiries"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("supplier_listings.id"), nullable=False)
    business_profile_id = Column(Integer, ForeignKey("business_profiles.id"), nullable=True)
    
    requester_company_name = Column(String(255), nullable=False)
    requester_name = Column(String(255), nullable=False)
    requester_email = Column(String(255), nullable=False)
    requester_phone = Column(String(50), nullable=False)
    
    product_interest = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    consent_given = Column(Boolean, default=True, nullable=False)
    consent_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
