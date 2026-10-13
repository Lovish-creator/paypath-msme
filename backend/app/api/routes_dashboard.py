from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.core.auth import get_current_business
from backend.app.models.business import BusinessProfile
from backend.app.schemas.dashboard import DashboardResponse
from backend.app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard_metrics(
    current_business: BusinessProfile = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return DashboardService.get_dashboard_metrics(db, business_profile_id=current_business.id)

