import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token

client = TestClient(app)
client.headers.update({"Authorization": f"Bearer {create_access_token({'sub': '1', 'email': 'demo@apexuniforms.in'})}"})



def test_download_case_preparation_report_pdf():
    resp = client.get("/api/cases/1/report/pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    content = resp.content
    assert len(content) > 3000
    assert content.startswith(b"%PDF")  # Valid PDF binary signature


def test_dashboard_metrics_consistency():
    resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_invoices_count"] >= 5
    assert data["total_outstanding_amount"] > 0
    assert data["total_overdue_amount"] > 0
    assert "₹" in data["formatted_total_outstanding"]
    assert "₹" in data["formatted_total_overdue"]
    assert len(data["stage_breakdown"]) == 8


def test_demo_reset_action():
    resp = client.post("/api/demo/reset")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["invoices_seeded"] == 5
    assert data["cases_seeded"] == 5
