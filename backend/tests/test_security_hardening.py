import pytest
import io
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import Settings, settings
from backend.app.core.security import create_access_token
from backend.app.services.document_extractor import DocumentExtractor

client = TestClient(app)
client.headers.update({"Authorization": f"Bearer {create_access_token({'sub': '1', 'email': 'demo@apexuniforms.in'})}"})


def test_production_configuration_validation():
    # 1. Weak Secret Key raises RuntimeError in production
    bad_secret_cfg = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="dev-insecure-secret-key-change-in-production-only",
        ALLOW_DEMO_RESET=False,
        ENABLE_DEMO_SEEDING=False,
        CORS_ORIGINS="https://paypath.in",
    )
    with pytest.raises(RuntimeError, match="FATAL SECURITY CONFIGURATION: Production deployment requires a secure"):
        bad_secret_cfg.validate_production_configuration()

    # 2. Demo reset enabled in production raises RuntimeError
    bad_demo_cfg = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a" * 35,
        ALLOW_DEMO_RESET=True,
        ENABLE_DEMO_SEEDING=False,
        CORS_ORIGINS="https://paypath.in",
    )
    with pytest.raises(RuntimeError, match="ALLOW_DEMO_RESET must be False in production"):
        bad_demo_cfg.validate_production_configuration()

    # 3. Demo seeding enabled in production raises RuntimeError
    bad_seed_cfg = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a" * 35,
        ALLOW_DEMO_RESET=False,
        ENABLE_DEMO_SEEDING=True,
        CORS_ORIGINS="https://paypath.in",
    )
    with pytest.raises(RuntimeError, match="ENABLE_DEMO_SEEDING must be False in production"):
        bad_seed_cfg.validate_production_configuration()

    # 4. Wildcard CORS in production raises RuntimeError
    bad_cors_cfg = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a" * 35,
        ALLOW_DEMO_RESET=False,
        ENABLE_DEMO_SEEDING=False,
        CORS_ORIGINS="*",
    )
    with pytest.raises(RuntimeError, match="Wildcard CORS origins are forbidden in production"):
        bad_cors_cfg.validate_production_configuration()

    # 5. Proper production configuration passes without error
    good_cfg = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="super-secure-production-random-token-here-32chars!",
        ALLOW_DEMO_RESET=False,
        ENABLE_DEMO_SEEDING=False,
        CORS_ORIGINS="https://paypath.in,https://app.paypath.in",
    )
    good_cfg.validate_production_configuration()  # should not raise


def test_upload_magic_bytes_validation():
    # Reject non-PDF file content even if filename is .pdf
    fake_pdf = b"NOT_A_REAL_PDF_HEADER"
    files = {"file": ("invoice.pdf", io.BytesIO(fake_pdf), "application/pdf")}
    resp = client.post("/api/invoices/extract-document", files=files)
    assert resp.status_code == 400
    assert "Invalid file format" in resp.json()["detail"]


def test_upload_oversized_file_validation(monkeypatch):
    # Temporarily set max upload to 100 bytes for testing
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_BYTES", 100)
    oversized_data = b"%PDF-1.4" + b"A" * 200
    files = {"file": ("big_invoice.pdf", io.BytesIO(oversized_data), "application/pdf")}
    resp = client.post("/api/invoices/extract-document", files=files)
    assert resp.status_code == 413
    assert "Invoice file size exceeds maximum limit" in resp.json()["detail"]


def test_document_extractor_no_synthetic_fabrication():
    # Extracting from empty/dummy text must return None for missing fields, not fake data
    text = "Some random text without any invoice number or amount."
    extracted = DocumentExtractor.parse_invoice_text(text, "dummy.pdf", "/tmp/dummy.pdf")
    
    assert extracted.invoice_number is None
    assert extracted.total_amount is None
    assert extracted.invoice_date is None
    assert extracted.buyer_name is None
    assert extracted.has_written_agreement is None
    assert extracted.agreed_credit_days is None


def test_cross_tenant_invoice_deletion_and_rules():
    # 1. Invoice with recorded payments cannot be deleted
    # Invoice 3 has paid_amount = 150000.00 > 0
    resp_paid = client.delete("/api/invoices/3")
    assert resp_paid.status_code == 400
    assert "Cannot delete invoice with recorded payments" in resp_paid.json()["detail"]

    # 2. Creating an invoice without payments and deleting it works
    create_payload = {
        "invoice_number": "INV-TEST-DEL-001",
        "buyer_name": "Test Delete Buyer",
        "invoice_date": "2026-08-01",
        "total_amount": 15000.0,
        "has_written_agreement": False,
    }
    create_resp = client.post("/api/invoices", json=create_payload)
    assert create_resp.status_code == 201
    inv_id = create_resp.json()["id"]

    # 3. Cross-tenant attempt: Another tenant registers and cannot delete business 1's invoice
    tenant2_reg = client.post("/api/auth/register", json={
        "email": "cross_tenant_test@company.in",
        "password": "Password123!",
        "full_name": "Cross Tenant User",
        "business_name": "Cross Tenant Corp",
        "enterprise_type": "micro",
        "state": "Delhi",
        "district": "New Delhi",
    })
    tenant2_token = tenant2_reg.json()["access_token"]
    tenant2_headers = {"Authorization": f"Bearer {tenant2_token}"}
    unauthorized_del = client.delete(f"/api/invoices/{inv_id}", headers=tenant2_headers)
    assert unauthorized_del.status_code == 404
    assert "Invoice not found or access denied" in unauthorized_del.json()["detail"]

    # 4. Delete invoice as legitimate owner
    del_resp = client.delete(f"/api/invoices/{inv_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "success"

    # Verify invoice is gone
    get_resp = client.get(f"/api/invoices/{inv_id}")
    assert get_resp.status_code == 404
