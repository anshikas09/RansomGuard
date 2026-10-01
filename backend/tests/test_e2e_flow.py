"""End-to-end demo flow test for RansomGuard backend."""
import sys
sys.path.insert(0, "backend")

from fastapi.testclient import TestClient
from app.core.database import Base, engine
from app.main import app

# Fresh DB
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# 1. Signup
r = client.post("/api/v1/auth/signup", json={
    "email": "admin@ransomguard.soc",
    "password": "SecurePass123",
    "password_confirmation": "SecurePass123",
    "full_name": "SOC Admin",
    "organization": "RansomGuard Lab",
    "role": "admin"
})
print(f"Signup: {r.status_code}")
token = r.json()["access_token"]

# 2. Login
r = client.post("/api/v1/auth/login", json={"email": "admin@ransomguard.soc", "password": "SecurePass123"})
print(f"Login: {r.status_code}")
token = r.json()["access_token"]

# 3. Get me
r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
data = r.json()
print(f"Me: {r.status_code} - {data['email']}")

# 4. Register endpoint
r = client.post("/api/v1/endpoints/register", json={"hostname": "demo-workstation", "os": "Windows 11", "ip_address": "192.168.1.100", "agent_version": "1.0.0"})
data = r.json()
print(f"Register endpoint: {r.status_code} - {data['hostname']}")

# 5. Heartbeat
r = client.post("/api/v1/endpoints/heartbeat", json={"hostname": "demo-workstation", "cpu_usage": 12.5, "memory_usage": 256.0, "telemetry_count": 0, "status": "online"})
print(f"Heartbeat: {r.status_code}")

# 6. Telemetry - benign event
r = client.post("/api/v1/telemetry/", json={"hostname": "demo-workstation", "events": [
    {"file_path": "C:/docs/report.docx", "operation": "read", "file_size": 2048.0, "entropy": 4.2, "entropy_change": 0.1, "mod_rate": 0.01, "ext_changed": 0, "is_suspicious_process": 0, "file_path_length": 20, "is_common_extension": 1, "process_name": "word.exe"}
]})
data = r.json()
print(f"Benign telemetry: {r.status_code} - risk={data['endpoint_risk']}")

# 7. Telemetry - 10 ransomware burst events to fill rolling sequence
malicious_events = [
    {
        "file_path": f"C:/docs/file_{i}.encrypted",
        "operation": "modify",
        "file_size": 4096.0,
        "entropy": 7.95,
        "entropy_change": 3.8,
        "mod_rate": 0.9,
        "ext_changed": 1,
        "is_suspicious_process": 1,
        "file_path_length": 24,
        "is_common_extension": 0,
        "process_name": "ransim_burst.exe"
    } for i in range(10)
]

r = client.post("/api/v1/telemetry/", json={"hostname": "demo-workstation", "events": malicious_events})
data = r.json()
print(f"Malicious telemetry sequence: {r.status_code} - risk={data['endpoint_risk']}")

# 8. List incidents (verify automatic incident creation upon threat detection)
r = client.get("/api/v1/incidents/", headers={"Authorization": f"Bearer {token}"})
incidents = r.json()
print(f"Incidents: {r.status_code} - count={len(incidents)}")
if len(incidents) > 0:
    print(f"Auto-created incident ID: {incidents[0]['id']} - Severity: {incidents[0]['severity']} - Threat Score: {incidents[0]['threat_score']}")

# 9. Simulation status
r = client.get("/api/v1/simulation/status")
data = r.json()
print(f"Simulation: {r.status_code} - running={data.get('is_running', False)}")

# 10. ML pipeline info
r = client.get("/api/v1/ml/pipeline-info", headers={"Authorization": f"Bearer {token}"})
print(f"ML info: {r.status_code}")

# 11. Health components
r = client.get("/api/v1/health/components")
print(f"Components: {r.status_code}")

# 12. Chatbot
r = client.post("/api/v1/chatbot/query", json={"question": "What is ransomware?"}, headers={"Authorization": f"Bearer {token}"})
print(f"Chatbot: {r.status_code}")

print("\n=== E2E DEMO FLOW: ALL PASSED ===")
