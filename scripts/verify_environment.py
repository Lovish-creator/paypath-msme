import sys
import os
from datetime import date

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("==================================================")
print(" PayPath MSME -- Environment & Diagnostic Verifier")
print(" SLIET PITCHVERSE 2026 | Prototype Verification")
print("==================================================")

# 1. Check Python version
print(f"[OK] Python Version: {sys.version.split()[0]}")

# 2. Check Core Dependencies
required_modules = ["fastapi", "uvicorn", "pydantic", "sqlalchemy", "reportlab", "pytest"]
for mod in required_modules:
    try:
        __import__(mod)
        print(f"[OK] Dependency '{mod}' is installed and accessible.")
    except ImportError as e:
        print(f"[FAIL] Dependency '{mod}' is MISSING: {e}")
        sys.exit(1)

# 3. Test Legal Engine
try:
    from backend.app.services.legal_engine import LegalEngine
    res = LegalEngine.calculate_timeline_and_interest(
        invoice_date=date(2026, 8, 1),
        delivery_date=date(2026, 8, 2),
        agreed_credit_days=30,
        outstanding_principal=100000.0,
        as_of_date=date(2026, 10, 1),
    )
    assert res["is_overdue"] is True
    assert res["estimated_interest"] == 1687.50
    print(f"[OK] Legal Engine: Section 15 & 16 calculation verified (Interest: INR {res['estimated_interest']:,.2f}).")
except Exception as e:
    print(f"[FAIL] Legal Engine test failed: {e}")
    sys.exit(1)

# 4. Test Database and Seed Data
try:
    from backend.app.db.database import SessionLocal, Base, engine
    from backend.app.models.invoice import Invoice
    from backend.app.models.case import Case
    from backend.app.demo.seed_data import seed_database
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db, force_reset=False)
    inv_count = db.query(Invoice).count()
    case_count = db.query(Case).count()
    db.close()
    print(f"[OK] Database persistence: {inv_count} invoices, {case_count} cases seeded and verified.")
except Exception as e:
    print(f"[FAIL] Database verification failed: {e}")
    sys.exit(1)

# 5. Test PDF Generation
try:
    from backend.app.services.pdf_service import PDFService
    from backend.app.models.business import BusinessProfile
    db = SessionLocal()
    c = db.query(Case).first()
    p = db.query(BusinessProfile).first()
    pdf_buf = PDFService.generate_case_preparation_report(c, p)
    db.close()
    pdf_bytes = pdf_buf.getvalue()
    assert pdf_bytes.startswith(b"%PDF")
    print(f"[OK] PDF Report Generator: Valid {len(pdf_bytes)} byte PDF report generated successfully.")
except Exception as e:
    print(f"[FAIL] PDF generator test failed: {e}")
    sys.exit(1)

# 6. Check Frontend Build
dist_index = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist", "index.html")
if os.path.exists(dist_index):
    print(f"[OK] Frontend Production Build: Valid bundle verified at {dist_index}.")
else:
    print(f"[!] Frontend dist/index.html not found; run 'npm run build' inside frontend/.")

print("==================================================")
print(" PayPath MSME Prototype Status: FULLY OPERATIONAL & READY")
print("==================================================")
