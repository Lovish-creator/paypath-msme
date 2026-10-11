import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_get_case_details():
    resp = client.get("/api/cases/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["reference_code"] == "CASE-INV-2026-0891"
    assert data["current_stage"] >= 1
    assert "evidence_items" in data
    assert len(data["evidence_items"]) >= 6
    assert "timeline" in data
    assert "completeness_summary" in data


def test_update_case_stage():
    # Update stage to 7 (Report Generated)
    stage_payload = {
        "current_stage": 7,
        "notes": "Evidence verified and pre-litigation package ready.",
    }
    resp = client.put("/api/cases/1/stage", json=stage_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_stage"] == 7
    assert data["stage_label"] == "Case-Preparation Report Generated"

    # Verify transition event was logged
    event_summaries = [ev["summary"] for ev in data["follow_up_events"]]
    assert any("Escalation Stage updated" in s for s in event_summaries)


def test_evidence_item_status_update():
    case_resp = client.get("/api/cases/2").json()  # Case 2 has missing delivery item
    missing_items = [it for it in case_resp["evidence_items"] if it["status"] == "missing"]
    assert len(missing_items) > 0
    item_id = missing_items[0]["id"]

    update_payload = {
        "status": "provided",
        "file_name": "transporter_lr_pod_copy.pdf",
        "notes": "Retrieved stamped LR copy from driver",
    }
    resp = client.put(f"/api/cases/2/evidence/{item_id}", json=update_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "provided"
    assert data["file_name"] == "transporter_lr_pod_copy.pdf"


def test_generate_reminders_and_formal_notice():
    # 1. Friendly reminder
    resp_friendly = client.post("/api/cases/1/reminders", json={"tone": "friendly"})
    assert resp_friendly.status_code == 200
    friendly_data = resp_friendly.json()
    assert "Friendly Payment Reminder" in friendly_data["notice_title"]
    assert friendly_data["has_statutory_citations"] is False

    # 2. Formal Notice
    resp_formal = client.post("/api/cases/1/reminders", json={"tone": "formal_notice"})
    assert resp_formal.status_code == 200
    formal_data = resp_formal.json()
    assert "Formal Demand Notice under Section 15 & 16" in formal_data["notice_title"]
    assert formal_data["has_statutory_citations"] is True
    assert "Section 16" in formal_data["body_markdown"]
    assert "Section 43B(h)" in formal_data["body_markdown"]
    assert "MSEFC" in formal_data["body_markdown"]
