from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

os.environ.setdefault("SAFETY_DB_PATH", str(Path("backend/test_safety_platform.db").resolve()))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.main import app, init_schema, seed_database  # noqa: E402


Path(os.environ["SAFETY_DB_PATH"]).unlink(missing_ok=True)
init_schema()
seed_database()
client = TestClient(app)


def token() -> str:
    res = client.post("/api/auth/login", json={"email": "admin@industrial.local", "password": "SafetyDemo!2026"})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {token()}"}


def test_health_and_auth() -> None:
    assert client.get("/api/health").status_code == 200
    me = client.get("/api/auth/me", headers=auth_headers())
    assert me.status_code == 200
    assert me.json()["role"] == "admin"


def test_mission_control_and_risk() -> None:
    headers = auth_headers()
    mission = client.get("/api/mission-control", headers=headers)
    assert mission.status_code == 200
    assert mission.json()["metrics"]["incidents"] > 0
    risk = client.get("/api/risk/compound", headers=headers)
    assert risk.status_code == 200
    assert "compound_risk_score" in risk.json()


def test_permit_review_and_rag() -> None:
    headers = auth_headers()
    review = client.post(
        "/api/permits/review",
        headers=headers,
        json={
            "permit_type": "hot_work",
            "zone_id": "zone_1",
            "work_description": "hot work welding with gas test",
            "controls": ["PPE", "isolation"],
            "simultaneous_work": True,
            "gas_test_value": 55,
        },
    )
    assert review.status_code == 200, review.text
    assert review.json()["risk_score"] >= 55
    assert review.json()["zone"] in {"Tank Farm", "Process Area", "Maintenance Bay", "Utilities", "Warehouse", "Control Room"}
    assert "required_controls" in review.json()
    rag = client.post("/api/knowledge/query", headers=headers, json={"query": "lockout tagout permit", "limit": 2})
    assert rag.status_code == 200
    assert "evidence" in rag.json()
    assert rag.json()["required_controls"]


def test_report_generation() -> None:
    headers = auth_headers()
    report = client.post("/api/reports/generate", headers=headers, json={"report_type": "executive"})
    assert report.status_code == 200, report.text
    assert report.json()["pdf"].endswith("/pdf")
    assert report.json()["summary"]["plant"]


def test_copilot_simulation_assets_workers_and_admin_users() -> None:
    headers = auth_headers()
    agent = client.post(
        "/api/agents/risk_intelligence/run",
        headers=headers,
        json={"goal": "Evaluate gas leak maintenance controls", "context": {"zone_id": "zone_tank_farm"}},
    )
    assert agent.status_code == 200, agent.text
    assert agent.json()["display"]["primary_action"]
    sim = client.post("/api/simulations/run", headers=headers, json={"scenario": "gas_leak", "zone_id": "zone_tank_farm", "intensity": 0.8})
    assert sim.status_code == 200, sim.text
    assert sim.json()["affected_zones"]
    assets = client.get("/api/assets", headers=headers)
    assert assets.status_code == 200
    assert assets.json()["summary"]["total"] > 0
    assert "health_status" in assets.json()["assets"][0]
    workers = client.get("/api/workers", headers=headers)
    assert workers.status_code == 200
    assert workers.json()["current_profile"]["role_definition"]["label"]
    users = client.get("/api/admin/users", headers=headers)
    assert users.status_code == 200
    assert "ehs_manager" in users.json()["roles"]
    cv = client.get("/api/computer-vision/status", headers=headers)
    assert cv.status_code == 200
    assert cv.json()["enabled"] is True
    assert cv.json()["summary"]["connected_cameras"] > 0
    assert cv.json()["detections"]
    cv_run = client.post("/api/computer-vision/run", headers=headers)
    assert cv_run.status_code == 200, cv_run.text
    assert cv_run.json()["inspection_id"].startswith("cv_")


def test_factory_dataset_upload_recalculates_risk() -> None:
    headers = auth_headers()
    csv_text = """zone,equipment,health_score,gas,temperature,pressure,vibration,permit_status,incident,severity,timestamp
Tank Farm,Solvent Pump A,42,78,83,9,8,open,Elevated gas detected during transfer,5,2026-07-22T10:00:00Z
Process Area,Reactor Agitator,68,15,64,5,3,approved,,1,2026-07-22T10:05:00Z
"""
    upload = client.post(
        "/api/factory/upload-dataset",
        headers=headers,
        json={"filename": "factory_sample.csv", "csv_text": csv_text, "replace_uploaded": True},
    )
    assert upload.status_code == 200, upload.text
    body = upload.json()
    assert body["rows_processed"] == 2
    assert body["inserted"]["equipment"] == 2
    assert body["risk_summary"]["max_uploaded_risk"] >= 80


def test_demo_factory_upload_rebuilds_site() -> None:
    headers = auth_headers()
    demo = client.get("/api/factory/demo-dataset", headers=headers)
    assert demo.status_code == 200, demo.text
    payload = demo.json()
    assert payload["rows"] >= 8
    upload = client.post(
        "/api/factory/upload-dataset",
        headers=headers,
        json={"filename": payload["filename"], "csv_text": payload["csv_text"], "replace_uploaded": True},
    )
    assert upload.status_code == 200, upload.text
    body = upload.json()
    assert body["factory"]["name"] == "Orion Specialty Polymers Unit-07"
    assert body["inserted"]["zones"] >= 8
    twin = client.get("/api/digital-twin", headers=headers)
    assert twin.status_code == 200
    assert twin.json()["plant"]["name"] == "Orion Specialty Polymers Unit-07"
    assert len(twin.json()["zones"]) >= 8
    assert twin.json()["routes"]
