# RansomGuard REST & WebSocket API Specification

All REST API endpoints are served under the `/api/v1` base route. Interactive OpenAPI / Swagger documentation is available at `http://localhost:8000/docs`.

---

## Authentication & Session Management

### `POST /api/v1/auth/signup`
Registers a new SOC user. If this is the first registered user, the system automatically assigns the `admin` role.
* **Request Body:**
  ```json
  {
    "email": "analyst@ransomguard.soc",
    "password": "SecurePassword123",
    "full_name": "Lead SOC Analyst",
    "organization": "Cyber Defense Unit",
    "role": "admin"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "access_token": "<jwt_token>",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "analyst@ransomguard.soc",
      "full_name": "Lead SOC Analyst",
      "organization": "Cyber Defense Unit",
      "role": "admin",
      "is_active": true
    }
  }
  ```

### `POST /api/v1/auth/login`
Authenticates user credentials and returns a signed JSON Web Token (JWT).
* **Request Body:**
  ```json
  {
    "email": "analyst@ransomguard.soc",
    "password": "SecurePassword123"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "access_token": "<jwt_token>",
    "token_type": "bearer",
    "user": { ... }
  }
  ```

### `GET /api/v1/auth/me`
Fetches authenticated user identity and role from session token.
* **Headers:** `Authorization: Bearer <jwt_token>`

### `POST /api/v1/auth/logout`
Terminates and invalidates the current session token in the database.

---

## Endpoint Fleet Management

### `GET /api/v1/endpoints/`
Lists all registered enterprise endpoints with live heartbeat and isolation status.
* **Headers:** `Authorization: Bearer <jwt_token>`
* **Response (200 OK):**
  ```json
  [
    {
      "id": 1,
      "hostname": "soc-workstation-alpha",
      "ip_address": "10.0.0.15",
      "os": "Windows 11 Pro",
      "agent_version": "1.0.0",
      "status": "online",
      "is_isolated": false,
      "current_risk": 0.0,
      "last_heartbeat": "2026-10-01T08:00:00Z"
    }
  ]
  ```

### `POST /api/v1/endpoints/register`
Registers or updates an endpoint agent.
* **Request Body:**
  ```json
  {
    "hostname": "soc-endpoint-vm01",
    "ip_address": "127.0.0.1",
    "os": "Windows Security Host",
    "agent_version": "1.0.0"
  }
  ```

### `POST /api/v1/endpoints/heartbeat`
Ingests periodic health heartbeats from endpoint agents.

### `POST /api/v1/endpoints/{id}/isolate`
Enacts or releases manual network isolation on an endpoint (Admin / SOC Analyst).
* **Request Body:**
  ```json
  {
    "isolated": true,
    "reason": "Suspicious burst activity detected"
  }
  ```

---

## Telemetry Ingestion & Stream

### `POST /api/v1/telemetry/`
Primary batch telemetry ingestion endpoint. Ingests events, computes feature vectors, executes ONNX inference, and applies risk heuristics.
* **Request Body:**
  ```json
  {
    "hostname": "soc-workstation-alpha",
    "simulation_id": "SIM-20260929080219-547",
    "reset_buffer": false,
    "events": [
      {
        "file_path": "./scratch/ransim_lab/safe_lab_doc_001.encrypted",
        "operation": "modify",
        "file_size": 2048,
        "entropy": 7.982,
        "entropy_change": 3.42,
        "mod_rate": 0.05,
        "ext_changed": 1,
        "is_suspicious_process": 1,
        "file_path_length": 55,
        "is_common_extension": 0,
        "process_name": "ransim_combined.exe"
      }
    ]
  }
  ```
* **Response (201 Created):**
  ```json
  {
    "status": "success",
    "ingested_count": 1,
    "endpoint_risk": 100.0,
    "incident_id": 1
  }
  ```

### `GET /api/v1/telemetry/recent`
Returns sliding window of recent telemetry events for chart visualization.
* **Query Parameters:** `limit` (default: 50, Dashboard uses 30)

### `GET /api/v1/telemetry/stats`
Returns total aggregate count of all telemetry events stored in the database.
* **Response (200 OK):** `{ "total_events": 198 }`

---

## Incident Management & Response

### `GET /api/v1/incidents/`
Returns all logged incidents sorted chronologically descending.
* **Headers:** `Authorization: Bearer <jwt_token>`

### `GET /api/v1/incidents/{incident_id}`
Returns granular forensic detail for a specific incident, including detection signals, affected file paths, behavior timeline, and response actions.

### `PATCH /api/v1/incidents/{incident_id}`
Updates an incident's triage status, adds analyst notes, or executes manual containment overrides.
* **Request Body:**
  ```json
  {
    "status": "resolved",
    "analyst_notes": "Verified safe test simulation; containment released.",
    "containment_action": "release_isolation"
  }
  ```

---

## Safe Simulation Lab

### `POST /api/v1/simulation/start`
Configures and launches a controlled filesystem behavioral simulation inside `scratch/ransim_lab/`.
* **Request Body:**
  ```json
  {
    "simulation_type": "combined",
    "number_of_files": 50,
    "modification_rate": 20.0,
    "extension_changes": true,
    "process_name": "ransim_combined.exe"
  }
  ```

### `POST /api/v1/simulation/stop`
Gracefully halts an active simulation and cleans up the sandbox workspace.

### `GET /api/v1/simulation/status`
Returns real-time status of the simulation runner (files touched, rate, live entropy delta, ML probability, threat score, detection and containment states).

---

## Machine Learning & Model Registry

### `GET /api/v1/ml/versions`
Lists all trained model versions and checkpoints in the registry.

### `GET /api/v1/ml/active`
Returns metadata, input tensor specifications, and training metrics for the currently loaded ONNX model.

### `POST /api/v1/ml/train`
Triggers model training pipeline (`train.py`) in the background (Admin only).

---

## AI Copilot Chatbot

### `POST /api/v1/chatbot/query`
Sends an investigation query to the RansomGuard Copilot assistant.
* **Request Body:**
  ```json
  {
    "query": "How do I triage Incident #1?",
    "context": { "incident_id": 1 }
  }
  ```

---

## Health & Demo Management

### `GET /api/v1/health`
System liveness and component connectivity status.

### `POST /api/v1/demo/reset`
Controlled reset operation for local demo and test data (Admin only). Clears simulation telemetry, test incidents, containment actions, and resets endpoints to unrestricted online state without removing registered users, models, or core configuration.

---

## Real-Time WebSocket Protocol

* **WebSocket URL:** `ws://<host>:8000/ws`
* **Incoming Events:** None (server-push)
* **Outgoing Event Payloads:**
  * `TELEMETRY_BATCH_INGESTED`: Streamed whenever a new telemetry batch is evaluated.
  * `INCIDENT_UPDATED`: Streamed whenever an incident is created, escalated, or contained.
  * `ENDPOINT_UPDATED`: Streamed when an endpoint heartbeat arrives or isolation status changes.
  * `SIMULATION_PROGRESS`: Streamed during active simulation runs.
  * `DEMO_DATA_RESET`: Streamed when demo data is reset.
