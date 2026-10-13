import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token

client = TestClient(app)
client.headers.update({"Authorization": f"Bearer {create_access_token({'sub': '1', 'email': 'demo@apexuniforms.in'})}"})



def test_supplier_discovery_matching():
    # Apex Uniforms is in garment_manufacturing, with purchasing interests in thread, fabric, buttons
    resp = client.get("/api/suppliers")
    assert resp.status_code == 200
    suppliers = resp.json()
    assert len(suppliers) >= 4
    
    # First returned items should match garment industry or thread tags
    top_supplier = suppliers[0]
    assert top_supplier["is_sponsored"] is True
    assert top_supplier["industry_category"] in ("garment_manufacturing", "packaging", "industrial_components")


def test_supplier_enquiry_consent_enforcement():
    # Fetch first supplier
    suppliers = client.get("/api/suppliers").json()
    sup_id = suppliers[0]["id"]

    # 1. Reject enquiry without explicit consent
    no_consent_payload = {
        "supplier_id": sup_id,
        "requester_company_name": "Apex Uniforms & Apparel",
        "requester_name": "Finance Lead",
        "requester_email": "finance@apexuniforms.in",
        "requester_phone": "+91 98765 43210",
        "product_interest": "Polyester Spun Thread 40/2",
        "message": "Interested in bulk pricing for 500 cones",
        "consent_given": False,  # Missing consent!
    }
    resp_no_consent = client.post(f"/api/suppliers/{sup_id}/enquiries", json=no_consent_payload)
    assert resp_no_consent.status_code == 400
    assert "Explicit user consent is mandatory" in resp_no_consent.json()["detail"]

    # 2. Accept enquiry with explicit consent
    consent_payload = dict(no_consent_payload)
    consent_payload["consent_given"] = True
    resp_success = client.post(f"/api/suppliers/{sup_id}/enquiries", json=consent_payload)
    assert resp_success.status_code == 201
    enquiry_data = resp_success.json()
    assert enquiry_data["supplier_id"] == sup_id
    assert enquiry_data["consent_given"] is True

    # 3. Check enquiry history for business
    resp_hist = client.get("/api/suppliers/enquiries/history")
    assert resp_hist.status_code == 200
    assert any(e["id"] == enquiry_data["id"] for e in resp_hist.json())

    # 4. Check advertiser view for that supplier
    resp_adv = client.get(f"/api/suppliers/{sup_id}/advertiser-leads")
    assert resp_adv.status_code == 200
    assert any(e["id"] == enquiry_data["id"] for e in resp_adv.json())
