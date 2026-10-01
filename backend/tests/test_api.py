import sys
import os

# Ensure backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from app.core.database import Base, engine
from app.main import app

# Create all database tables before tests run
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    # Optionally drop tables after tests
    # Base.metadata.drop_all(bind=engine)

client = TestClient(app)

# ==================== Root & Health ====================

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_health_check_endpoint():
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert "components" in response.json()

# ==================== Auth ====================

def test_auth_signup_flow():
    payload = {
        "email": "test_analyst@ransomguard.soc",
        "password": "Password123",
        "password_confirmation": "Password123",
        "full_name": "Test Analyst",
        "organization": "Security Lab",
        "role": "soc_analyst"
    }
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code in (200, 400)  # 200 OK or 400 if already exists
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test_analyst@ransomguard.soc"

def test_auth_login_flow():
    payload = {
        "email": "test_analyst@ransomguard.soc",
        "password": "Password123"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_auth_login_wrong_password():
    payload = {
        "email": "test_analyst@ransomguard.soc",
        "password": "WrongPassword1"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401

def test_auth_me_without_token():
    response = client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)

def test_auth_me_with_token():
    login_res = client.post("/api/v1/auth/login", json={
        "email": "test_analyst@ransomguard.soc",
        "password": "Password123"
    })
    if login_res.status_code == 200:
        token = login_res.json()["access_token"]
        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "test_analyst@ransomguard.soc"

# ==================== Endpoints ====================

def test_endpoint_registration():
    payload = {
        "hostname": "test-vm-host",
        "os": "Windows 11",
        "ip_address": "127.0.0.1",
        "agent_version": "1.0.0"
    }
    response = client.post("/api/v1/endpoints/register", json=payload)
    assert response.status_code == 200
    assert response.json()["hostname"] == "test-vm-host"

def test_endpoint_heartbeat():
    payload = {
        "hostname": "test-vm-host",
        "cpu_usage": 5.3,
        "memory_usage": 112.0,
        "telemetry_count": 0,
        "status": "online"
    }
    response = client.post("/api/v1/endpoints/heartbeat", json=payload)
    assert response.status_code == 200

def test_endpoint_list_requires_auth():
    response = client.get("/api/v1/endpoints/")
    assert response.status_code in (401, 403)

# ==================== Telemetry ====================

def test_telemetry_ingestion():
    payload = {
        "hostname": "test-vm-host",
        "events": [
            {
                "file_path": "C:/lab/doc_001.docx",
                "operation": "modify",
                "file_size": 4096.0,
                "entropy": 7.8,
                "entropy_change": 3.2,
                "mod_rate": 0.1,
                "ext_changed": 0,
                "is_suspicious_process": 1,
                "file_path_length": 22,
                "is_common_extension": 1,
                "process_name": "ransim_burst.exe"
            }
        ]
    }
    response = client.post("/api/v1/telemetry/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["ingested_count"] == 1
    assert "endpoint_risk" in data

# ==================== Simulation ====================

def test_simulation_status():
    response = client.get("/api/v1/simulation/status")
    assert response.status_code == 200
    assert "is_running" in response.json()
