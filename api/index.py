import os
import sys

# Ensure repository root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.main import app
from backend.app.db.database import Base, engine, SessionLocal
from backend.app.models.invoice import Invoice
from backend.app.demo.seed_data import seed_database

# Ensure database tables and initial demonstration data exist in the serverless environment
try:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = db.query(Invoice).count()
        if count == 0:
            seed_database(db, force_reset=False)
    finally:
        db.close()
except Exception as e:
    print(f"[Vercel] Serverless DB auto-init warning: {e}")
