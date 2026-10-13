import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import Base, get_db
from backend.app.demo.seed_data import seed_database

from backend.app.core.security import create_access_token, hash_password
from backend.app.models.user import User
from backend.app.models.business import BusinessProfile

# Use a file-based temporary sqlite db or isolated engine for tests
TEST_DB_URL = "sqlite:///./test_paypath.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def init_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSession()
    seed_database(db, force_reset=True)

    # Also seed Tenant B (Isolated MSME for security testing)
    tenant_b_profile = BusinessProfile(
        id=2,
        name="Ludhiana Metal Components Pvt Ltd",
        enterprise_type="small",
        udyam_number="UDYAM-PB-12-0099881",
        pan="AABCL9988K",
        gstin="03AABCL9988K1Z2",
        state="Punjab",
        district="Ludhiana",
        industry_category="industrial_components",
        purchasing_interests="steel,tooling",
        contact_email="sales@ludhianametal.in",
        contact_phone="+91 98765 11223",
    )
    db.add(tenant_b_profile)
    db.flush()

    tenant_b_user = User(
        id=2,
        email="tenantb@ludhianametal.in",
        hashed_password=hash_password("Password123!"),
        full_name="Ludhiana Admin",
        phone="+91 98765 11223",
        business_profile_id=tenant_b_profile.id,
    )
    db.add(tenant_b_user)
    db.flush()
    tenant_b_profile.owner_user_id = tenant_b_user.id
    db.commit()

    db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)
    import os
    if os.path.exists("./test_paypath.db"):
        try:
            os.remove("./test_paypath.db")
        except Exception:
            pass


@pytest.fixture(autouse=True)
def apply_db_override():
    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield


@pytest.fixture
def demo_token():
    return create_access_token({"sub": "1", "email": "demo@apexuniforms.in"})


@pytest.fixture
def auth_headers(demo_token):
    return {"Authorization": f"Bearer {demo_token}"}


@pytest.fixture
def client(auth_headers):
    c = TestClient(app)
    c.headers.update(auth_headers)
    return c


@pytest.fixture
def unauth_client():
    return TestClient(app)


@pytest.fixture
def tenant_b_token():
    return create_access_token({"sub": "2", "email": "tenantb@ludhianametal.in"})


@pytest.fixture
def tenant_b_client(tenant_b_token):
    c = TestClient(app)
    c.headers.update({"Authorization": f"Bearer {tenant_b_token}"})
    return c

