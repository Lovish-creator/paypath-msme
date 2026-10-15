from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.database import get_db
from backend.app.demo.seed_data import seed_database
from backend.app.models.invoice import Invoice
from backend.app.models.case import Case

router = APIRouter(prefix="/demo", tags=["Demo Management"])


@router.post("/reset")
def reset_demo_data(db: Session = Depends(get_db)):
    """
    Development-only endpoint to reseed sample data.
    Strictly blocked in production environments and when ALLOW_DEMO_RESET is False.
    """
    if settings.ENVIRONMENT.lower() == "production" or not settings.ALLOW_DEMO_RESET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo data reset is strictly prohibited in production or when ALLOW_DEMO_RESET is disabled.",
        )

    # Extra defense-in-depth: check if database URL targets production
    db_url_lower = settings.DATABASE_URL.lower()
    if "prod" in db_url_lower or ("postgres" in db_url_lower and "localhost" not in db_url_lower and "127.0.0.1" not in db_url_lower):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo data reset cannot execute against external or production database targets.",
        )

    seed_database(db, force_reset=True)
    invoices_count = db.query(Invoice).count()
    cases_count = db.query(Case).count()
    return {
        "status": "success",
        "message": "Demo data reset successfully to canonical development sample baseline.",
        "invoices_seeded": invoices_count,
        "cases_seeded": cases_count,
    }


@router.get("/status")
def get_demo_status(db: Session = Depends(get_db)):
    if settings.ENVIRONMENT.lower() == "production" or not settings.ALLOW_DEMO_RESET:
        return {
            "is_demo_mode": False,
            "total_invoices": 0,
            "total_cases": 0,
            "active_company": None,
        }
    invoices_count = db.query(Invoice).count()
    cases_count = db.query(Case).count()
    return {
        "is_demo_mode": True,
        "total_invoices": invoices_count,
        "total_cases": cases_count,
        "active_company": "Apex Uniforms & Apparel (Sample MSME)",
    }
