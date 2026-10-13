from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from backend.app.schemas.supplier import BusinessProfileResponse


class UserRegisterRequest(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.\+\-]+@[\w\.\-]+\.\w+$", description="Valid email address")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    full_name: Optional[str] = "MSME Owner"
    phone: Optional[str] = None
    business_name: Optional[str] = None
    enterprise_type: Optional[str] = "micro"
    udyam_number: Optional[str] = ""
    state: Optional[str] = "Punjab"
    district: Optional[str] = "Sangrur"


class UserLoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.\+\-]+@[\w\.\-]+\.\w+$")
    password: str



class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    business_profile_id: Optional[int] = None
    business_profile: Optional[BusinessProfileResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
