from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from backend.app.core.config import settings
from backend.app.db.database import Base, engine, SessionLocal
from backend.app.demo.seed_data import seed_database
from backend.app.models.invoice import Invoice
from backend.app.api.routes_health import router as health_router
from backend.app.api.routes_auth import router as auth_router
from backend.app.api.routes_dashboard import router as dashboard_router
from backend.app.api.routes_invoices import router as invoices_router
from backend.app.api.routes_cases import router as cases_router
from backend.app.api.routes_suppliers import router as suppliers_router
from backend.app.api.routes_demo import router as demo_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("paypath")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Enforce production security rules
    settings.validate_production_configuration()

    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    if settings.ENABLE_DEMO_SEEDING:
        db = SessionLocal()
        try:
            count = db.query(Invoice).count()
            if count == 0:
                logger.info("Initializing database with sample demonstration records...")
                seed_database(db, force_reset=False)
        finally:
            db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="PayPath MSME — Delayed Payment Escalation, Traceable Legal Engine & B2B Supplier Discovery",
    lifespan=lifespan,
)

# Enable CORS for trusted frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please check server logs."},
    )


# Register API Routers
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(invoices_router, prefix="/api")
app.include_router(cases_router, prefix="/api")
app.include_router(suppliers_router, prefix="/api")
app.include_router(demo_router, prefix="/api")



@app.get("/")
def root():
    return {
        "app": "PayPath MSME Backend API",
        "docs_url": "/docs",
        "api_health": "/api/health",
        "status": "online",
    }
