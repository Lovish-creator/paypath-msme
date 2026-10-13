import pytest
from datetime import date
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.security import create_access_token

client = TestClient(app)
client.headers.update({"Authorization": f"Bearer {create_access_token({'sub': '1', 'email': 'demo@apexuniforms.in'})}"})



def test_list_invoices():
    response = client.get("/api/invoices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    # Primary demo case should be present
    assert any(inv["invoice_number"] == "INV-2026-0891" for inv in data)


def test_create_invoice_and_initial_invariants():
    new_inv = {
        "invoice_number": "INV-TEST-9999",
        "buyer_name": "Test Industrial Corporation",
        "buyer_gstin": "03AAACT1111Q1Z4",
        "invoice_date": "2026-09-01",
        "delivery_date": "2026-09-03",
        "has_written_agreement": True,
        "agreed_credit_days": 30,
        "total_amount": 150000.0,
        "goods_services_description": "Custom machining parts",
    }
    response = client.post("/api/invoices", json=new_inv)
    assert response.status_code == 201
    data = response.json()
    assert data["invoice_number"] == "INV-TEST-9999"
    assert data["total_amount"] == 150000.0
    assert data["paid_amount"] == 0.0
    assert data["outstanding_balance"] == 150000.0
    assert data["status"] in ("issued", "overdue")
    assert data["case"] is not None
    assert data["case"]["reference_code"] == "CASE-INV-TEST-9999"


def test_prevent_duplicate_invoice_number():
    dup_inv = {
        "invoice_number": "INV-2026-0891",  # already exists in seed data
        "buyer_name": "Duplicate Tester",
        "invoice_date": "2026-09-01",
        "total_amount": 50000.0,
    }
    response = client.post("/api/invoices", json=dup_inv)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_partial_and_full_payment_lifecycle():
    # Fetch invoice 1
    resp = client.get("/api/invoices")
    inv = [i for i in resp.json() if i["invoice_number"] == "INV-2026-0891"][0]
    inv_id = inv["id"]
    initial_balance = inv["outstanding_balance"]  # 485000.0

    # 1. Reject payment greater than outstanding balance
    invalid_pay = {
        "amount": initial_balance + 5000.0,
        "payment_date": "2026-10-01",
        "reference_number": "UTR-OVERPAY-1",
    }
    resp_over = client.post(f"/api/invoices/{inv_id}/payments", json=invalid_pay)
    assert resp_over.status_code == 400
    assert "exceeds outstanding balance" in resp_over.json()["detail"]

    # 2. Record partial payment
    part_pay = {
        "amount": 200000.0,
        "payment_date": "2026-10-02",
        "reference_number": "UTR-TEST-PART-1",
        "payment_mode": "NEFT",
    }
    resp_part = client.post(f"/api/invoices/{inv_id}/payments", json=part_pay)
    assert resp_part.status_code == 201

    # Verify updated balance
    inv_updated = client.get(f"/api/invoices/{inv_id}").json()
    assert inv_updated["paid_amount"] == 200000.0
    assert inv_updated["outstanding_balance"] == initial_balance - 200000.0
    assert inv_updated["status"] in ("partially_paid", "overdue")

    # 3. Record remaining payment to fully settle
    remaining = inv_updated["outstanding_balance"]
    full_pay = {
        "amount": remaining,
        "payment_date": "2026-10-05",
        "reference_number": "UTR-TEST-FULL-2",
        "payment_mode": "RTGS",
    }
    resp_full = client.post(f"/api/invoices/{inv_id}/payments", json=full_pay)
    assert resp_full.status_code == 201

    # Verify fully paid state
    inv_final = client.get(f"/api/invoices/{inv_id}").json()
    assert inv_final["paid_amount"] == initial_balance
    assert inv_final["outstanding_balance"] == 0.0
    assert inv_final["status"] == "paid"
