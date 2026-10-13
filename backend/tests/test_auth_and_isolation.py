import io
import pytest
from backend.app.schemas.invoice import InvoiceCreate


def test_unauthenticated_requests_rejected(unauth_client):
    """Verify that unauthenticated requests to protected endpoints return 401 Unauthorized"""
    res_inv = unauth_client.get("/api/invoices")
    assert res_inv.status_code == 401
    assert "Authentication required" in res_inv.json()["detail"]

    res_dash = unauth_client.get("/api/dashboard")
    assert res_dash.status_code == 401

    res_case = unauth_client.get("/api/cases/1")
    assert res_case.status_code == 401

    res_pdf = unauth_client.get("/api/cases/1/report/pdf")
    assert res_pdf.status_code == 401


def test_user_registration_and_login_flow(unauth_client):
    """Verify user registration, token acquisition, and login verification"""
    reg_payload = {
        "email": "newsupplier@punjabtextiles.in",
        "password": "SecurePassword123!",
        "full_name": "Harpreet Singh",
        "phone": "+91 98765 99887",
        "business_name": "Punjab Textiles & Weaving",
        "enterprise_type": "micro",
        "udyam_number": "UDYAM-PB-12-0055112",
        "state": "Punjab",
        "district": "Amritsar",
    }
    reg_res = unauth_client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "newsupplier@punjabtextiles.in"
    assert reg_data["user"]["full_name"] == "Harpreet Singh"
    assert reg_data["user"]["business_profile"]["name"] == "Punjab Textiles & Weaving"

    # Duplicate registration should fail
    dup_res = unauth_client.post("/api/auth/register", json=reg_payload)
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"]

    # Login with valid credentials
    login_res = unauth_client.post(
        "/api/auth/login",
        json={"email": "newsupplier@punjabtextiles.in", "password": "SecurePassword123!"},
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data

    # Login with invalid password
    bad_login = unauth_client.post(
        "/api/auth/login",
        json={"email": "newsupplier@punjabtextiles.in", "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401
    assert "Invalid email or password" in bad_login.json()["detail"]


def test_cross_tenant_data_isolation(client, tenant_b_client):
    """
    CRITICAL SECURITY TEST:
    Verify that Tenant A and Tenant B have strictly isolated data boundaries.
    Tenant B cannot view, read, update, or download Tenant A's invoices, cases, or reports.
    """
    # 1. Tenant A (Apex Uniforms, id=1) has seed invoices
    tenant_a_invoices = client.get("/api/invoices").json()
    assert len(tenant_a_invoices) >= 5
    tenant_a_inv = tenant_a_invoices[0]
    inv_id = tenant_a_inv["id"]
    case_id = tenant_a_inv["case"]["id"]

    # 2. Tenant B (Ludhiana Metal, id=2) lists invoices -> should NOT see Tenant A's invoices!
    tenant_b_invoices = tenant_b_client.get("/api/invoices").json()
    assert len(tenant_b_invoices) == 0  # Honest empty state for Tenant B!

    # 3. Tenant B attempts to fetch Tenant A's invoice directly by ID -> MUST return 404/denied
    trespass_inv = tenant_b_client.get(f"/api/invoices/{inv_id}")
    assert trespass_inv.status_code == 404
    assert "not found or access denied" in trespass_inv.json()["detail"]

    # 4. Tenant B attempts to fetch Tenant A's case details -> MUST return 404/denied
    trespass_case = tenant_b_client.get(f"/api/cases/{case_id}")
    assert trespass_case.status_code == 404
    assert "not found or access denied" in trespass_case.json()["detail"]

    # 5. Tenant B attempts to download Tenant A's PDF dossier -> MUST return 404/denied
    trespass_pdf = tenant_b_client.get(f"/api/cases/{case_id}/report/pdf")
    assert trespass_pdf.status_code == 404

    # 6. Tenant B creates their own invoice
    new_b_inv = {
        "invoice_number": "INV-LUDH-001",
        "buyer_name": "Punjab Tractor Heavy Engineering",
        "buyer_gstin": "03AAAPL9988Z1Z5",
        "invoice_date": "2026-09-10",
        "total_amount": 125000.0,
        "has_written_agreement": True,
        "agreed_credit_days": 30,
        "goods_services_description": "Cast iron axle components",
    }
    create_b_res = tenant_b_client.post("/api/invoices", json=new_b_inv)
    assert create_b_res.status_code == 201

    # Tenant B now sees 1 invoice
    tenant_b_list = tenant_b_client.get("/api/invoices").json()
    assert len(tenant_b_list) == 1
    assert tenant_b_list[0]["invoice_number"] == "INV-LUDH-001"

    # Tenant A lists invoices -> does NOT see Tenant B's invoice!
    tenant_a_updated = client.get("/api/invoices").json()
    assert not any(i["invoice_number"] == "INV-LUDH-001" for i in tenant_a_updated)


def test_invoice_document_extraction_endpoint(client):
    """Test invoice document extraction route with simulated PDF content"""
    # Create a minimal in-memory PDF
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    c.drawString(100, 750, "TAX INVOICE")
    c.drawString(100, 720, "Invoice Number: INV-EXTRACTION-771")
    c.drawString(100, 700, "Date: 15/08/2026")
    c.drawString(100, 680, "Buyer: Northern Engineering Works")
    c.drawString(100, 660, "GSTIN: 03AAACN1234F1Z8")
    c.drawString(100, 640, "Total Amount: Rs. 84,500.00")
    c.save()
    pdf_buffer.seek(0)

    files = {"file": ("test_invoice.pdf", pdf_buffer.getvalue(), "application/pdf")}
    res = client.post("/api/invoices/extract-document", files=files)
    assert res.status_code == 200
    data = res.json()

    assert data["invoice_number"] == "INV-EXTRACTION-771"
    assert data["buyer_gstin"] == "03AAACN1234F1Z8"
    assert data["total_amount"] == 84500.0
    assert data["confidence_score"] > 0.5
    assert "test_invoice.pdf" in data["source_file_name"]
