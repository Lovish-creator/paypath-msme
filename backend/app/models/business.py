from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.db.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    enterprise_type = Column(String(50), nullable=False, default="micro")  # micro, small, medium
    udyam_number = Column(String(100), nullable=False, default="")
    pan = Column(String(50), nullable=True)
    gstin = Column(String(50), nullable=True)
    state = Column(String(100), nullable=False, default="Punjab")
    district = Column(String(100), nullable=False, default="Sangrur")
    industry_category = Column(String(100), nullable=False, default="garment_manufacturing")
    purchasing_interests = Column(String(500), nullable=False, default="thread,fabric,buttons,zippers,packaging")
    contact_email = Column(String(255), nullable=False, default="info@apexuniforms.in")
    contact_phone = Column(String(50), nullable=False, default="+91 98765 43210")
    owner_user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    users = relationship("User", back_populates="business_profile", foreign_keys="[User.business_profile_id]")
    invoices = relationship("Invoice", back_populates="business_profile", cascade="all, delete-orphan")

