from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.demo.seed_data import seed_database
from backend.app.models.invoice import Invoice
from backend.app.models.case import Case

router = APIRouter(prefix="/demo", tags=["Demo Management"])


@router.post("/reset")
def reset_demo_data(db: Session = Depends(get_db)):
    seed_database(db, force_reset=True)
    invoices_count = db.query(Invoice).count()
    cases_count = db.query(Case).count()
    return {
        "status": "success",
        "message": "Demo data reset successfully to canonical SLIET PitchVerse 2026 test baseline.",
        "invoices_seeded": invoices_count,
        "cases_seeded": cases_count,
    }


@router.get("/status")
def get_demo_status(db: Session = Depends(get_db)):
    invoices_count = db.query(Invoice).count()
    cases_count = db.query(Case).count()
    return {
        "is_demo_mode": True,
        "total_invoices": invoices_count,
        "total_cases": cases_count,
        "active_company": "Apex Uniforms & Apparel (Sample MSME)",
    }
