from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.db.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    business_profile_id = Column(Integer, ForeignKey("business_profiles.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    business_profile = relationship(
        "BusinessProfile",
        back_populates="users",
        foreign_keys=[business_profile_id]
    )
