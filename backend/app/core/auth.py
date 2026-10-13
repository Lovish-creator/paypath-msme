from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.db.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.user import User
from backend.app.models.business import BusinessProfile

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Validates bearer token and returns the authenticated User.
    Raises HTTP 401 if token is missing or invalid.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in to access your enterprise workspace.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    try:
        user_id_int = int(user_id)
        user = db.query(User).filter(User.id == user_id_int).first()
    except (ValueError, TypeError):
        user = db.query(User).filter(User.email == str(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    return user


def get_current_business(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BusinessProfile:
    """
    Returns the BusinessProfile workspace for the authenticated User.
    If none exists, automatically initializes a dedicated profile.
    """
    if current_user.business_profile_id:
        profile = db.query(BusinessProfile).filter(BusinessProfile.id == current_user.business_profile_id).first()
        if profile:
            return profile

    # Auto-initialize an isolated profile if not attached
    new_profile = BusinessProfile(
        name=f"{current_user.full_name}'s Enterprise",
        enterprise_type="micro",
        udyam_number="",
        state="Punjab",
        district="Sangrur",
        industry_category="general_manufacturing",
        purchasing_interests="raw_materials,packaging",
        contact_email=current_user.email,
        contact_phone=current_user.phone or "+91 00000 00000",
        owner_user_id=current_user.id,
    )
    db.add(new_profile)
    db.flush()

    current_user.business_profile_id = new_profile.id
    db.commit()
    db.refresh(new_profile)
    return new_profile


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Returns the authenticated user if token is present, else None."""
    if not credentials or not credentials.credentials:
        return None
    try:
        return get_current_user(credentials=credentials, db=db)
    except HTTPException:
        return None
