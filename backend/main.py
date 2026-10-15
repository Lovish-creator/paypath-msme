import os
import sys

# Ensure backend package and repository root are on sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(backend_dir)
for path in (root_dir, backend_dir):
    if path not in sys.path:
        sys.path.insert(0, path)

from backend.app.main import app
from backend.app.db.database import Base, engine, SessionLocal
from backend.app.models.invoice import Invoice
from backend.app.demo.seed_data import seed_database

# Ensure tables and seed data exist in serverless environment
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
