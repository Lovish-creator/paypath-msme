from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from backend.app.db.database import get_db
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.auth import get_current_user
from backend.app.models.user import User
from backend.app.models.business import BusinessProfile
from backend.app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.lower().strip()
    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An account with email '{email_clean}' already exists.",
        )

    # 1. Create BusinessProfile for this tenant workspace
    b_name = payload.business_name.strip() if payload.business_name else f"{payload.full_name.strip()}'s Enterprise"
    profile = BusinessProfile(
        name=b_name,
        enterprise_type=payload.enterprise_type or "micro",
        udyam_number=payload.udyam_number.strip() if payload.udyam_number else "",
        state=payload.state or "Punjab",
        district=payload.district or "Sangrur",
        industry_category="general_manufacturing",
        purchasing_interests="raw_materials,packaging",
        contact_email=email_clean,
        contact_phone=payload.phone or "+91 00000 00000",
    )
    db.add(profile)
    db.flush()

    # 2. Create User
    user = User(
        email=email_clean,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        phone=payload.phone,
        business_profile_id=profile.id,
    )
    db.add(user)
    db.flush()

    profile.owner_user_id = user.id
    db.commit()
    db.refresh(user)
    db.refresh(profile)

    # 3. Create Token
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated.",
        )

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post("/logout")
def logout():
    return {"status": "success", "message": "Successfully signed out."}
