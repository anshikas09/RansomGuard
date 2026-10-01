# RansomGuard

**AI-Powered Behavioral Ransomware Detection & Safe Auto-Containment Platform**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009485?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.2-20232A?style=flat-square&logo=react&logoColor=61DAFB)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX_Runtime-Inference-005CED?style=flat-square&logo=onnx&logoColor=white)](https://onnxruntime.ai/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.3-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)

> **Safety Notice:** RansomGuard is an educational and defensive cybersecurity engineering platform designed for controlled laboratory simulation. It executes behavioral analysis strictly within designated sandbox directories (`scratch/ransim_lab/`) and **never** modifies, encrypts, or deletes user or system files.

---

## 1. Hero / Project Summary

RansomGuard is a cloud-ready, local SOC-oriented ransomware defense platform that monitors filesystem behavior, extracts behavioral telemetry, evaluates temporal activity using an LSTM neural network exported to ONNX, combines deep-learning inference with heuristic behavioral risk signals, creates deduplicated incidents, and safely contains simulated ransomware activity inside a controlled laboratory environment.

Traditional endpoint security often relies heavily on static malware signatures, hashes, and known indicators of compromise (IOCs). RansomGuard addresses the evasion capabilities of modern ransomware by focusing on **dynamic behavioral telemetry**—analyzing temporal file mutation velocity, Shannon entropy shifts, extension anomalies, and suspicious process execution patterns in real time.

---

## 2. Why RansomGuard?

Static signature-based antivirus solutions struggle against novel, obfuscated, or compiled-on-demand ransomware strains. A single byte change alters an executable's SHA-256 hash, bypassing traditional hash-matching controls.

RansomGuard shifts the defense paradigm from *what an executable looks like* to *what a running process does*. By analyzing filesystem telemetry across rolling time windows, RansomGuard identifies the operational fingerprints inherent to ransomware attacks:

* **High-Frequency Mutation Bursts:** Legitimate applications rarely modify dozens of distinct documents within a single second.
* **Shannon Entropy Spikes:** Unencrypted plain-text, source code, and office documents exhibit structured, lower entropy ($\approx 3.0 - 5.0$). Modern cryptographic algorithms produce encrypted payloads with near-maximum Shannon entropy ($\approx 7.5 - 8.0$).
* **Extension & Header Manipulation:** Rapid substitution of file extensions (e.g., `.docx` $\rightarrow$ `.encrypted`) paired with high entropy indicates active ransom extortion.
* **Temporal Sequence Dynamics:** Individual benign operations (such as saving a single document) can appear suspicious in isolation. An LSTM temporal sequence model evaluates the progression of 10 consecutive filesystem events to distinguish benign administrative bursts from algorithmic encryption sweeps.

---

## 3. What RansomGuard Does

RansomGuard operates an end-to-end, multi-stage detection and mitigation pipeline:

```
Controlled Simulation Lab / Monitored Filesystem
                        │
                        ▼
           Filesystem Telemetry Collector
                        │
                        ▼
        8-Dimensional Feature Extraction Vector
                        │
                        ▼
         10-Event Rolling Sequence Buffer (N, 10, 8)
                        │
                        ▼
      ONNX Runtime LSTM Sequence Classification
                        │
                        ▼
             Raw ML Probability [0.0 - 1.0]
                        │
                        ▼
       Heuristic Behavioral Engine [0 - 100%]
                        │
                        ▼
        Composite Threat Score & Severity Mapping
                        │
                        ▼
     Incident Engine & Session Deduplication
                        │
                        ▼
    Automated Safe Containment (Process Kill + Host Isolation)
                        │
                        ▼
  SQLite / PostgreSQL Persistence & Audit Logging
                        │
                        ▼
     Real-Time Full-Duplex WebSocket Broadcast
                        │
                        ▼
          React SOC Command Center Dashboard
```

1. **Telemetry Ingestion:** Filesystem events (`create`, `modify`, `delete`, `rename`) are captured by endpoint sensors.
2. **Feature Extraction:** Raw events are transformed into normalized 8-dimensional feature vectors.
3. **Sequence Construction:** A rolling window maintains the last 10 operations per endpoint to capture temporal trends.
4. **ONNX Deep Learning Inference:** A 2-layer LSTM model evaluates the 10-event sequence and outputs an anomaly probability.
5. **Hybrid Risk Engine:** Combines the neural network output with real-time heuristic signals (entropy delta, burst rate, suspicious naming) to produce a composite Threat Score.
6. **Incident Deduplication:** Correlates multiple telemetry events belonging to a single attack episode into one actionable incident record.
7. **Safe Auto-Containment:** Terminates the offending simulation process, marks the simulated endpoint as isolated, and moves altered files to quarantine.
8. **Real-Time SOC Visualization:** Streams telemetry, threat scores, and incident lifecycle states to an interactive SOC dashboard via WebSockets.

---

## 4. Key Features

* **Behavioral Filesystem Monitoring:** Ingests live filesystem operations without relying on pre-existing malware signatures.
* **Temporal LSTM Sequence Classifier:** Evaluates rolling windows of 10 consecutive events using PyTorch-trained neural networks.
* **Low-Latency ONNX Runtime Inference:** Deploys models in optimized ONNX format for low-latency inference without PyTorch runtime overhead.
* **Separated Multi-Layer Risk Architecture:** Distinctly reports ML Probability, Heuristic Behavioral Score, and Composite Threat Score to provide transparent, explainable SOC telemetry.
* **Attack Episode Incident Deduplication:** Prevents SOC alert fatigue by consolidating rapid bursts of suspicious telemetry into a single logical incident.
* **Safe Automated Containment:** Enacts immediate simulated process termination, network quarantine isolation, and file quarantine within the laboratory workspace.
* **Real-Time SOC Command Center:** Dark-themed React dashboard with interactive Recharts risk timelines, incident feeds, and endpoint status matrices.
* **Full-Duplex WebSocket Updates:** Pushes instant updates to analyst dashboards on telemetry ingestion, incident status changes, and containment triggers.
* **Comprehensive Endpoint Fleet Management:** Tracks endpoint heartbeats, distinguishing agent network connectivity (`online`/`offline`) from security containment (`is_isolated`).
* **Controlled Simulation Lab:** Built-in web console for generating parameter-controlled benign and ransomware-like filesystem workloads.
* **Role-Based Access Control (RBAC):** Protects administrative routes and containment controls with JWT authentication and granular roles (`admin`, `soc_analyst`, `viewer`).
* **Structured Audit Logging:** Records every authentication attempt, incident status change, and containment action in an immutable database audit log.

---

## 5. System Architecture

```mermaid
flowchart TD
    subgraph Lab ["Controlled Lab Environment"]
        Sim["Simulation Lab UI"] -->|"Safe Operations"| Sandbox["Sandbox (scratch/ransim_lab)"]
        Agent["Watchdog Endpoint Agent"] -->|"File Events"| Sandbox
    end

    subgraph Ingestion ["FastAPI Ingestion Gateway"]
        Agent -->|"Batch Telemetry"| TelemAPI["Telemetry API (/api/v1/telemetry)"]
        Sim -->|"Simulation Events"| TelemAPI
    end

    subgraph Pipeline ["Detection & Decision Pipeline"]
        TelemAPI --> FE["Feature Extractor (8 Features)"]
        FE --> Buffer["Rolling Sequence Buffer (10 x 8)"]
        Buffer --> ONNX["ONNX LSTM Runner (ransomware_detector.onnx)"]
        ONNX --> MLScore["ML Probability (0.0 - 1.0)"]

        TelemAPI --> Heuristics["Behavioral Analyzer (Entropy, Velocity, Extensions)"]
        Heuristics --> BehavScore["Behavioral Score (0 - 100%)"]

        MLScore --> RiskEngine["Modular Risk Engine"]
        BehavScore --> RiskEngine

        RiskEngine --> CompositeScore["Composite Threat Score (0 - 100%)"]
        CompositeScore --> Decision{"Threat Score Threshold?"}

        Decision -->|"< 80%"| Monitor["Log & Monitor"]
        Decision -->|">= 80%"| Incident["Create & Deduplicate Incident"]
        Decision -->|">= 90%"| Containment["Execute Safe Auto-Containment"]
    end

    subgraph Persistence ["Data & Security Layer"]
        Monitor --> DB[("Database (SQLite / PostgreSQL)")]
        Incident --> DB
        Containment --> DB
        DB --> Audit["Audit Logs"]
    end

    subgraph SOC ["SOC Analyst Experience"]
        DB --> WSManager["WebSocket Manager"]
        WSManager -->|"Live Telemetry & Alerts"| WSStream["WebSocket Stream (ws://host/ws)"]
        WSStream --> Dashboard["React SOC Command Center"]
        Dashboard --> Copilot["Analyst Copilot Chatbot"]
    end
```

---

## 6. Detection Pipeline — Detailed

### Step 1 — Event Collection
Filesystem events (`create`, `modify`, `delete`, `rename`) are captured using the Python `watchdog` library or ingested directly through the simulation runner. Each event captures the target path, file size, process metadata, and timestamp.

### Step 2 — Feature Extraction
Raw filesystem events are converted into an 8-dimensional numerical feature vector:

| Index | Feature Name | Type | Description |
| :---: | :--- | :---: | :--- |
| `0` | `file_size` | Float | Size of the affected file in bytes |
| `1` | `entropy` | Float | Shannon entropy of the file payload ($0.0 - 8.0$) |
| `2` | `entropy_change` | Float | Difference in Shannon entropy compared to pre-modification state |
| `3` | `mod_rate` | Float | Time interval between consecutive file operations (seconds) |
| `4` | `ext_changed` | Binary | `1` if file extension was changed/substituted, `0` otherwise |
| `5` | `is_suspicious_process` | Binary | `1` if executing binary matches known attack signatures/patterns |
| `6` | `file_path_length` | Float | Length of target filesystem path in characters |
| `7` | `is_common_extension` | Binary | `1` for common extensions (`.docx`, `.pdf`, `.xlsx`), `0` for unusual extensions |

Shannon entropy is calculated over byte distribution:
$$H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$

### Step 3 — Temporal Sequence Buffer
Individual operations are assembled into temporal sequences of shape $(N, 10, 8)$, where $10$ represents the rolling history of consecutive filesystem events on that endpoint. If fewer than 10 events have occurred, the sequence is left-padded with zero-vectors. Features are normalized using `StandardScaler` fitted during pipeline training.

### Step 4 — LSTM Sequence Model
The neural network architecture is defined in [`ml_pipeline/train.py`](ml_pipeline/train.py):
* **Input Layer:** Shape `(batch_size, 10, 8)`
* **LSTM Backbone:** 2 stacked LSTM layers, `hidden_size = 128`, `batch_first = True`, `dropout = 0.3`
* **Dense Layer 1:** Fully connected layer (`128` $\rightarrow$ `64`) with ReLU activation and `Dropout(0.3)`
* **Dense Layer 2 (Output):** Fully connected layer (`64` $\rightarrow$ `1`) with Sigmoid activation outputting probability in $[0.0, 1.0]$

### Step 5 — ONNX Runtime Inference
The trained PyTorch model is exported to ONNX format (opset 11) with dynamic batch dimensions. The FastAPI backend loads `ransomware_detector.onnx` via `onnxruntime.InferenceSession`, enabling cross-platform, multi-threaded inference without Python GIL bottlenecks.

### Step 6 — Behavioral Heuristic Scoring
To prevent false negatives and provide defense-in-depth, [`backend/app/incidents/risk_engine.py`](backend/app/incidents/risk_engine.py) computes an independent Behavioral Score ($0 - 100\%$):
* **Event Frequency:** If file velocity $> 10.0$ ops/sec $\rightarrow \mathbf{+15\%}$
* **Entropy Delta:** If Shannon entropy delta $> 2.0 \rightarrow \mathbf{+35\%}$
* **Extension Manipulation:** If file extension was modified $\rightarrow \mathbf{+25\%}$
* **Process Context:** If process signal is flagged suspicious $\rightarrow \mathbf{+25\%}$

### Step 7 — Final Composite Threat Score
The composite Threat Score combines the baseline ML score with behavioral adjustments:
$$\text{Base Score} = \text{ML Probability} \times 100$$
$$\text{Threat Score} = \min(100.0, \text{Base Score} + \text{Heuristic Adjustments})$$
* Frequency $> 10$ ops/sec: $+10$
* Entropy Delta $> 2.0$: $+15$
* Extensions Changed $> 3$: $+10$
* Suspicious Process Context: $+20$

### Step 8 — Incident Classification & Severity Thresholds
* **LOW Severity:** Threat Score $< 30.0\%$ (Action: `MONITOR`)
* **MEDIUM Severity:** Threat Score $30.0\% - 59.9\%$ (Action: `MONITOR`)
* **HIGH Severity:** Threat Score $60.0\% - 79.9\%$ (Action: `MONITOR`)
* **CRITICAL Severity:** Threat Score $\ge 80.0\%$ (Action: `ALERT` / `CONTAIN`)

### Step 9 — Automated Safe Containment
When the Threat Score reaches or exceeds the containment threshold ($90.0\%$):
1. **Process Mitigation:** Issues a safe termination signal for the simulation process (`kill_process`).
2. **Network Isolation:** Flags the endpoint as isolated (`is_isolated = True`) while preserving agent heartbeat communication with the SOC.
3. **File Quarantine:** Simulates file quarantine by isolating modified sandbox files in `scratch/quarantine/`.
4. **Audit Logging:** Emits an immutable audit log entry documenting containment execution timestamp and triggering threat indicators.

---

## 7. Machine Learning / AI Pipeline

The machine learning subsystem in `ml_pipeline/` handles dataset generation, feature scaling, sequence windowing, model training, and baseline benchmarking:

```
Synthetic Event Generator (dataset.py)
                   │
                   ▼
  Session-Based Sequence Builder (sequences.py)
                   │
                   ▼
     StandardScaler Fitting (features.py)
                   │
                   ▼
  Session-Stratified Split: 70% Train / 15% Val / 15% Test
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
Classical ML Baselines   PyTorch LSTM (train.py)
  - Logistic Regression      │
  - Random Forest (100)      ▼
                         ONNX Export (opset 11)
                             │
                             ▼
                         Model Evaluation (evaluate.py)
```

### Dataset Generation & Session Stratification
To prevent temporal data leakage, [`ml_pipeline/sequences.py`](ml_pipeline/sequences.py) groups events by unique execution session IDs before generating sequences. Train, validation, and test sets are split **by session** rather than randomly slicing across individual events, ensuring that the model is evaluated strictly on unseen attack sessions.

---

## 8. Model Evaluation & Benchmark Results

The trained ONNX LSTM model was evaluated against the held-out synthetic test set (`X_test.npy`, `y_test.npy`):

| Evaluation Metric | Measured Score | Evaluation Notes |
| :--- | :---: | :--- |
| **Accuracy** | **100.00%** | Measured on held-out synthetic session split |
| **Precision** | **100.00%** | Zero false positives on synthetic benign workloads |
| **Recall** | **100.00%** | All synthetic ransomware sequences detected |
| **F1 Score** | **100.00%** | Harmonic mean of precision and recall |
| **ROC-AUC** | **1.0000** | Perfect separation on synthetic test set |
| **ONNX vs PyTorch Drift** | **$< 1.2 \times 10^{-7}$** | Numerical parity verified between PyTorch and ONNX |

> **IMPORTANT EVALUATION DISCLAIMER:**
> These results are measured strictly within the project's **controlled synthetic laboratory dataset**. They must **NOT** be interpreted as a claim of 100% detection accuracy against real-world, in-the-wild ransomware. Synthetic benchmarks feature structured, well-delineated operational boundaries. Real-world corporate environments introduce noise, legitimate high-entropy operations (compressed archives, video rendering, encrypted databases), and adversarial evasion techniques that present distinct detection challenges.

---

## 9. Baseline Model Comparison

To assess the value of temporal sequence modeling, classical machine learning baselines were evaluated on the identical synthetic benchmark (features flattened across the 10-event window to $N \times 80$ dimensions):

| Model Architecture | Input Representation | Accuracy | F1 Score | ROC-AUC | Inference Runtime |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Logistic Regression** | Flattened Window $(N, 80)$ | $100.00\%$ | $100.00\%$ | $1.0000$ | CPU Classical |
| **Random Forest (100 Trees)** | Flattened Window $(N, 80)$ | $100.00\%$ | $100.00\%$ | $1.0000$ | CPU Ensemble |
| **RansomGuard LSTM (ONNX)** | Temporal Sequence $(N, 10, 8)$ | **100.00%** | **100.00%** | **1.0000** | **ONNX Optimized** |

While all three models achieve clean separation on synthetic data, the **LSTM sequence architecture** maintains memory across variable event lengths and captures the chronological order of operations (e.g., file read $\rightarrow$ rapid rewrite $\rightarrow$ rename), which classical static classifiers cannot natively represent without heavy feature engineering.

---

## 10. Safe Simulation Lab

The Simulation Lab allows security analysts and students to safely observe ransomware behavior and test the detection pipeline without executing live malware.

### Safety Design Principles
* **Sandbox Confinement:** All operations are restricted to `scratch/ransim_lab/`. Target directories outside this boundary are rejected by path validation guards.
* **Controlled Process Names:** Simulations execute under explicit test process identifiers (`rapid_worker.exe`, `ransim_burst.exe`, `ransim_combined.exe`).
* **Synthetic Encryption:** Simulates high entropy using random byte generation rather than destructive encryption keys.
* **No Network Propagation:** The simulation does not perform network scanning, port binding, or lateral movement.

### Validated Regression Scenarios

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CONTROLLED SIMULATION SCENARIOS                       │
├──────────────────┬─────────────────┬──────────────────┬─────────────────────┤
│ Metric / State   │ Test A: Benign  │ Test B: Burst    │ Test C: Ransomware  │
├──────────────────┼─────────────────┼──────────────────┼─────────────────────┤
│ Simulation Type  │ Rapid Mod       │ Rapid Mod Burst  │ Combined Attack     │
│ File Targets     │ 10 files        │ 50 files         │ 50 files            │
│ Execution Rate   │ 2.0 ops/sec     │ 30.0 ops/sec     │ 20.0 ops/sec        │
│ Process Name     │ rapid_worker    │ rapid_worker     │ ransim_combined     │
│ High Entropy?    │ No (Normal)     │ No (Normal)      │ Yes (> 7.5 Shannon) │
│ Extension Alter? │ No (.docx)      │ No (.docx)       │ Yes (.encrypted)    │
│ ML Probability   │ ~0%             │ ~0%              │ 100%                │
│ Behavioral Score │ 0%              │ ~15%             │ 100%                │
│ Final Threat     │ 0% (LOW)        │ ~10% (LOW)       │ 100% (CRITICAL)     │
│ Incidents Made   │ 0               │ 0                │ 1 (Deduplicated)    │
│ Containment?     │ None (MONITOR)  │ None (MONITOR)   │ Auto-Contained      │
└──────────────────┴─────────────────┴──────────────────┴─────────────────────┘
```

* **Test A (Benign Burst):** Simulates routine text editing across 10 files. Correctly classified as normal; no alerts or containment.
* **Test B (High-Speed Benign Modification):** Simulates a high-velocity script editing 50 files at 30 ops/sec without encryption or extension modifications. The ML probability remains ~0%, the behavioral velocity heuristic registers slight activity (~15%), and the final composite threat remains low (~10%); no incidents are triggered and no containment is executed.
* **Test C (Combined Ransomware Pattern):** Simulates full ransomware behavior across 50 files at 20 ops/sec, pairing rapid modifications with high Shannon entropy payloads and `.encrypted` extension renaming. Triggers 100% ML and behavioral scores, creates **one logical incident**, terminates the simulation process, and isolates the host.

---

## 11. Incident Lifecycle & Deduplication

In a typical ransomware outbreak, a single malicious process may modify thousands of files within minutes. A naive detection engine would generate a separate incident ticket for every file event, overwhelming SOC analysts with alert fatigue.

RansomGuard implements **Session-Level Incident Deduplication**:

```
Telemetry Batch (50 File Events)
              │
              ▼
   Risk Threshold Crossed (>= 80%)
              │
              ▼
 Check Active Incidents for Endpoint
   ├── Existing Incident Found? ──► Append Detection Signals & Elevate Score
   └── No Active Incident?     ──► Create 1 New Logical Incident Record
              │
              ▼
   Execute Auto-Containment (>= 90%)
              │
              ▼
 Transition Incident State: NEW ──► CONTAINED ──► RESOLVED
```

During Test C (50 simulated files resulting in 90 telemetry operations), RansomGuard generated **exactly 1 deduplicated incident** (`Incident #1`), preserving an accurate, uncluttered incident queue.

---

## 12. Endpoint Fleet Management

RansomGuard maintains visibility over multiple enterprise endpoints through an agent architecture:

* **Endpoint Registration:** Endpoints register via `POST /api/v1/endpoints/register`, storing hostname, operating system, IP address, and agent version.
* **Heartbeat Monitoring:** Agents send periodic pings to update `last_heartbeat`. If an agent misses heartbeats, its status transitions to `offline`.
* **Connectivity vs Containment State Model:**
  * `status`: Indicates agent heartbeat connectivity (`online` vs `offline`).
  * `is_isolated`: Indicates host security containment (`True` vs `False`).
* **Why Isolated Endpoints Remain "Online":** When an endpoint is contained due to ransomware detection, its network communication is quarantined at the host level, but the RansomGuard agent **retains command-and-control connectivity** with the SOC console. This allows security analysts to perform remote triage, gather forensics, and issue un-isolation commands.
* **Dashboard Presentation:** The SOC console displays mutually exclusive host states:
  $$\text{Total Hosts} = \text{Online (Unrestricted)} + \text{Isolated} + \text{Offline}$$
  $$\mathbf{8} = \mathbf{7\ \text{Online}} + \mathbf{1\ \text{Isolated}} + \mathbf{0\ \text{Offline}}$$

---

## 13. SOC Dashboard Command Center

The frontend provides an interactive, dark-themed operations center built with React 18 and Tailwind CSS:

* **Dashboard (`/dashboard`):** Real-time command center displaying active/contained incident metrics, endpoint operational distribution, interactive Recharts risk timeline, severity distribution donut chart, and live incident stream.
* **Endpoints (`/endpoints`):** Fleet inventory table showing real-time agent status, operating system, IP address, risk scores, and manual isolation override toggles.
* **Incidents (`/incidents`):** Comprehensive incident feed filterable by severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) and status (`active`, `contained`, `resolved`).
* **Incident Detail (`/incidents/:id`):** Deep-dive forensic view providing temporal behavior timelines, affected file lists, detected entropy signals, model explanations, analyst investigation notes, and containment audit trails.
* **Model Center (`/models`):** Machine learning dashboard displaying active ONNX model version, architecture parameters, confusion matrix, ROC-AUC curves, and retrain triggers.
* **Simulation Lab (`/simulation-lab`):** Interactive testing workbench for configuring and launching safe simulation scenarios (file counts, modification rates, entropy generation, process names).
* **System Health (`/health`):** Operational health monitoring for the FastAPI backend, database connections, and WebSocket pub/sub status.
* **Onboarding Wizard (`/onboarding`):** Guided walk-through for new analysts and endpoint agent setup.
* **Copilot Chatbot Drawer:** Context-aware SOC assistant drawer providing instant advice on incident triage, ransomware mechanics, and platform status.

---

## 14. Security Design & RBAC

* **Authentication:** Stateless JSON Web Tokens (JWT) signed with HMAC-SHA256 (`HS256`).
* **Password Hashing:** Passwords hashed with `bcrypt` using cryptographic salt rounds.
* **Role-Based Access Control (RBAC):**
  * `admin`: Full administrative access (user management, model retraining, manual containment overrides, demo reset).
  * `soc_analyst`: Incident triage, analyst notes, simulation execution, and investigation views.
  * `viewer`: Read-only access to dashboard metrics and reports.
* **Input & Path Validation:** All file paths received in telemetry or simulation requests are validated to prevent directory traversal attacks (`../`).
* **Sandbox Boundaries:** Simulation endpoints reject any execution path outside the designated laboratory directory.
* **Immutable Audit Trail:** All critical operations (`USER_SIGNUP`, `USER_LOGIN`, `AUTOMATED_CONTAINMENT_EXECUTED`, `INCIDENT_UPDATED`, `DEMO_DATA_RESET`) are logged to the `audit_logs` table.

---

## 15. Safety Guarantee

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LABORATORY SAFETY GUARANTEE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. RansomGuard NEVER executes real malware binaries.                       │
│ 2. RansomGuard NEVER targets, encrypts, or modifies user documents.        │
│ 3. RansomGuard NEVER targets Windows or Linux operating system files.       │
│ 4. All simulation operations are strictly confined to scratch/ransim_lab/.  │
│ 5. Simulated encryption uses in-memory random byte streams.                 │
│ 6. Process termination affects only processes started by the simulation lab.│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 16. Data Architecture & Persistence

RansomGuard uses SQLAlchemy ORM with multi-database support:
* **Development Default:** SQLite (`sqlite:///./ransomguard.db`) with `check_same_thread=False` for zero-configuration local execution.
* **Production Ready:** PostgreSQL (`postgresql://user:pass@host:5432/ransomguard`) with connection pooling (`pool_size=10`, `max_overflow=20`).

### Database Entity Model
* `users`: Authentication records, email, bcrypt password hash, organization, and RBAC role.
* `sessions`: Active JWT sessions with expiration tracking.
* `endpoints`: Monitored hosts, hostnames, agent versions, IP addresses, connectivity status, and isolation flags.
* `endpoint_heartbeats`: Historical heartbeat logs for agent availability monitoring.
* `telemetry_events`: Granular filesystem events with feature vectors, entropy metrics, process names, and ML probabilities.
* `incidents`: Security incident records with composite threat scores, severity bands, affected files, and response actions.
* `containment_actions`: Records of automated or manual containment actions executed on endpoints.
* `audit_logs`: Immutable security audit log tracking user and system actions.
* `threats`: Correlated threat records linked to specific processes and endpoints.
* `model_versions`: Registry of trained ML model versions, architectures, and evaluation metrics.
* `training_runs`: Historical records of model training sessions, loss metrics, and hyperparameters.
* `alerts`: System notifications and SOC alert broadcasts.
* `chatbot_conversations`: Conversation history for the RansomGuard Copilot assistant.

---

## 17. REST API Overview

All API routes are served under `/api/v1`. Interactive Swagger documentation is accessible at `http://localhost:8000/docs`.

| Route Prefix | Primary Endpoints | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| **`/api/v1/auth`** | `POST /signup`, `POST /login`, `GET /me`, `POST /logout` | JWT user registration, session login, and profile | Mixed |
| **`/api/v1/endpoints`** | `GET /`, `POST /register`, `POST /heartbeat`, `POST /{id}/isolate` | Fleet inventory, agent registration, heartbeats, manual isolation | Bearer JWT |
| **`/api/v1/telemetry`** | `POST /`, `GET /recent`, `GET /stats` | Batch telemetry ingestion, sliding-window feed, total statistics | Mixed |
| **`/api/v1/incidents`** | `GET /`, `GET /{id}`, `PATCH /{id}` | Incident feed, forensic incident detail, status updates, notes | Bearer JWT |
| **`/api/v1/simulation`** | `POST /start`, `POST /stop`, `GET /status` | Simulation lab execution, real-time status monitoring | Bearer JWT |
| **`/api/v1/ml`** | `GET /versions`, `GET /active`, `POST /train` | Model registry, active ONNX metadata, training triggers | Bearer JWT (Admin) |
| **`/api/v1/chatbot`** | `POST /query`, `GET /history` | Copilot AI SOC analyst assistant queries | Bearer JWT |
| **`/api/v1/health`** | `GET /`, `GET /detailed` | Health check for backend, database, and inference engine | None |
| **`/api/v1/demo`** | `POST /reset` | Safe local reset for test incidents and telemetry | Bearer JWT (Admin) |

---

## 18. Real-Time Communication Protocol

Real-time telemetry and alerts stream over WebSockets at `ws://localhost:8000/ws`.

### Broadcast Event Types
* `TELEMETRY_BATCH_INGESTED`: Emitted upon processing incoming filesystem events. Contains endpoint ID, hostname, event count, max threat score, and severity.
* `INCIDENT_UPDATED`: Emitted when an incident is created, elevated, or updated. Contains incident ID, threat score, severity, and containment status.
* `ENDPOINT_UPDATED`: Emitted when endpoint connectivity or isolation status changes.
* `SIMULATION_PROGRESS`: Emitted periodically during active simulations with files touched, mutation rate, and live entropy metrics.
* `DEMO_DATA_RESET`: Emitted when an administrator triggers a demo data reset, instructing all active dashboards to refresh immediately.

---

## 19. Project Structure

```text
ransomguard/
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI route handlers (auth, telemetry, incidents, etc.)
│   │   ├── core/                 # Database connection, config, WebSocket manager
│   │   ├── incidents/            # Risk scoring engine and severity calculation
│   │   ├── ml/                   # ONNX Runtime inference runner
│   │   ├── models/               # SQLAlchemy ORM entity definitions
│   │   ├── schemas/              # Pydantic request/response validation models
│   │   ├── security/             # JWT auth, password hashing, and RBAC guards
│   │   └── main.py               # FastAPI application entrypoint and CORS setup
│   ├── tests/                    # PyTest test suite (API, risk engine, E2E)
│   ├── Dockerfile                # Backend container definition
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── public/                   # Static HTML and favicon assets
│   ├── src/
│   │   ├── components/           # Navbar, Sidebar, ChatbotDrawer
│   │   ├── contexts/             # AuthContext (JWT management)
│   │   ├── pages/                # Dashboard, Endpoints, SimulationLab, ModelCenter, etc.
│   │   ├── services/             # Axios API client and WebSocket service
│   │   ├── App.tsx               # Route definitions and navigation layout
│   │   └── index.tsx             # React DOM entrypoint
│   ├── Dockerfile                # Frontend container definition
│   ├── package.json              # React dependencies and scripts
│   └── tsconfig.json             # TypeScript compiler configuration
├── ml_pipeline/
│   ├── dataset.py                # Synthetic dataset generation
│   ├── features.py               # 8-feature extraction and StandardScaler serialization
│   ├── sequences.py              # 10-event sequence assembly and session-aware splitting
│   ├── train.py                  # PyTorch LSTM training and ONNX export (opset 11)
│   ├── evaluate.py               # Model evaluation and confusion matrix generation
│   └── baseline.py               # Logistic Regression and Random Forest benchmarks
├── models/
│   ├── ransomware_detector.onnx  # Deployed ONNX LSTM neural network (848 KB)
│   ├── scaler.pkl                # Serialized StandardScaler artifact
│   ├── X_test.npy                # Held-out evaluation feature test set
│   └── y_test.npy                # Held-out evaluation label test set
├── endpoint_agent/
│   ├── agent.py                  # Lightweight endpoint monitoring daemon
│   ├── containment.py            # Local process kill and quarantine logic
│   ├── feature_extractor.py      # Local feature extraction from file events
│   ├── inference.py              # Local edge inference runner
│   └── config.yaml               # Agent configuration
├── scripts/
│   ├── setup.ps1                 # Automated environment, dependency, and artifact verifier
│   ├── start-ransomguard.ps1     # One-command backend and frontend launcher
│   └── start-agent.ps1           # Endpoint agent launcher
├── docs/
│   ├── API.md                    # Detailed API specification
│   ├── ARCHITECTURE.md           # Architecture diagrams and design details
│   ├── ML_GUIDE.md               # Guide to model training and ONNX export
│   ├── USER_GUIDE.md             # SOC analyst operational guide
│   └── screenshots/              # UI screenshot directory (.gitkeep)
├── .env.example                  # Safe environment variable template
├── .gitignore                    # Air-tight security and artifact ignore rules
├── docker-compose.yml            # Multi-container orchestration (Postgres, API, UI)
└── README.md                     # Comprehensive platform documentation
```

---

## 20. Installation & Getting Started

### System Requirements
* **Operating System:** Windows 10/11, macOS, or Linux
* **Python:** Python 3.10+ (Python 3.12 recommended)
* **Node.js:** Node.js 18+ and npm
* **PowerShell:** PowerShell 5.1+ (on Windows)

---

### Windows One-Command Startup (Recommended)

Clone the repository and launch the platform:

```powershell
git clone https://github.com/anshikas09/RansomGuard.git
cd RansomGuard\frontend
npm start
```

The automated launcher (`scripts/start-ransomguard.ps1` via `setup.ps1`):
1. Detects system Python and provisions `.venv` if not already present.
2. Verifies backend dependencies (`uvicorn`, `fastapi`, `torch`, `onnxruntime`, etc.) and installs missing packages.
3. Validates that the ONNX model (`models/ransomware_detector.onnx`) and scaler (`models/scaler.pkl`) exist.
4. Auto-initializes the SQLite database and safe simulation directory (`scratch/ransim_lab/`).
5. Starts the FastAPI backend service on `http://127.0.0.1:8000`.
6. Launches the React development server on `http://localhost:3000`.
7. Automatically opens the SOC Command Center in your default web browser.

---

### Manual Startup (Cross-Platform)

#### 1. Backend Service
```bash
# From project root
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

# Start FastAPI backend
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Frontend Development Server
```bash
# In a separate terminal
cd frontend
npm install
npm run start:react
```

### Application URLs
* **SOC Command Center Dashboard:** [http://localhost:3000](http://localhost:3000)
* **FastAPI Backend REST API:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Interactive API Documentation (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 21. Environment Configuration

Copy `.env.example` to `.env` in the project root:

```bash
cp .env.example .env
```

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./ransomguard.db` | Database connection string (SQLite or PostgreSQL) |
| `JWT_SECRET` | *(Random 32-byte secret)* | HMAC key used to sign and verify JSON Web Tokens |
| `JWT_EXPIRATION_MINUTES`| `1440` | Token expiration lifetime (24 hours) |
| `BACKEND_URL` | `http://localhost:8000` | Backend API base URL |
| `LOG_LEVEL` | `INFO` | Python logging severity level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed frontend origins for CORS headers |
| `MODEL_PATH` | `./models/ransomware_detector.onnx` | Path to active ONNX model weights |
| `SCALER_PATH` | `./models/scaler.pkl` | Path to serialized StandardScaler |
| `SIMULATION_DIRECTORY` | `./scratch/ransim_lab` | Workspace directory for safe simulation testing |
| `ALERT_THRESHOLD` | `0.80` | Threat score threshold for incident alerting ($80\%$) |
| `CONTAINMENT_THRESHOLD`| `0.90` | Threat score threshold for automated containment ($90\%$) |

---

## 22. Docker Deployment

RansomGuard includes multi-container orchestration via Docker Compose:

```bash
# Build and start PostgreSQL, FastAPI Backend, and React Frontend
docker-compose up --build
```

### Services Initialized
* `postgres`: PostgreSQL 14 Alpine container on port `5432` with persistent volume `postgres_data`.
* `backend`: FastAPI server running on Python 3.12-slim exposed on port `8000`.
* `frontend`: Node.js 20 Alpine container serving the React application on port `3000`.

---

## 23. Testing & Verification

RansomGuard features an automated test suite verifying backend API endpoints, RBAC permissions, risk scoring logic, and end-to-end telemetry ingestion:

### Running Backend Tests
```powershell
pytest backend/tests
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.5, pytest-9.1.1, pluggy-1.6.0
rootdir: RansomGuard
collected 15 items

backend\tests\test_api.py ............                                   [ 80%]
backend\tests\test_risk_engine.py ...                                    [100%]

============================== 15 passed in 17.42s ============================
```

### Testing Frontend Build
```bash
cd frontend
npm run build
```
Output:
```text
Creating an optimized production build...
Compiled successfully.
File sizes after gzip:
  198.87 kB  build\static\js\main.fa91f817.js
  5.7 kB     build\static\css\main.c80e76c4.css
```

---

## 24. 5-Minute SOC Demonstration Walkthrough

Follow this step-by-step walkthrough to demonstrate RansomGuard during technical interviews, portfolio evaluations, or college defenses:

### Step 1: Login & Access Command Center
1. Open [http://localhost:3000](http://localhost:3000) in your browser.
2. Sign in with your registered analyst account or click **Sign Up** (the first registered account automatically receives the `admin` role).
3. The **SOC Command Center** loads, displaying active endpoints, incident cards, and live telemetry feeds.

### Step 2: Open Simulation Lab
1. In the left navigation sidebar, click **Simulation Lab**.
2. Notice the target safety directory indicator: `scratch/ransim_lab/`.

### Step 3: Execute Test A (Benign Baseline)
1. Select **Rapid File Modification**.
2. Set **Target File Count:** `10`.
3. Set **Modification Rate:** `2 ops/sec`.
4. Click **Run Simulation**.
5. **Observation:** Files are created and modified. The AI probability remains $\mathbf{0\%}$, behavioral score is $\mathbf{0\%}$, detection status is **NORMAL**, and containment is **MONITORING**.

### Step 4: Execute Test B (High-Speed Modification Burst)
1. Select **Rapid File Modification**.
2. Set **Target File Count:** `50`.
3. Set **Modification Rate:** `30 ops/sec`.
4. Click **Run Simulation**.
5. **Observation:** Velocity increases to 30 ops/sec. ML probability remains ~0%. Behavioral heuristics register slight activity ($\approx 15\%$), and the final composite threat remains low ($\approx 10\%$). Detection status remains **NORMAL**, containment remains **MONITORING**, and no incidents are triggered.

### Step 5: Execute Test C (Ransomware Attack & Auto-Containment)
1. Select **Combined (Entropy + Rapid Mod + Extension Change)**.
2. Set **Target File Count:** `50`.
3. Set **Modification Rate:** `20 ops/sec`.
4. Check **Extension Changes** (`.encrypted`).
5. Click **Run Simulation**.
6. **Observation:** High-entropy payloads and extension renaming rapidly elevate the ONNX LSTM model probability to $\mathbf{100\%}$. The Threat Score reaches $\mathbf{100\%}$ (**CRITICAL**).
7. Detection status immediately transitions to **RANSOMWARE DETECTED**, and containment transitions to **CONTAINED**.

### Step 6: Verify SOC Dashboard & Incident Investigation
1. Navigate to **SOC Dashboard**.
2. Observe that **Contained Incidents** increments by $1$, while **Active Incidents** remains $0$ because the threat was immediately neutralized.
3. In the **Severity Distribution** chart, view the Critical threat breakdown.
4. Click **Incidents** in the sidebar, click into the newly created incident, and inspect:
   * Suspected Process: `ransim_combined.exe`
   * Detection Signals: High Shannon Entropy ($> 7.5$), Extension Renaming (`.encrypted`).
   * Executed Containment: Process terminated, endpoint isolated, files quarantined.

---

## 25. Screenshots Directory (Placeholders)

UI screenshot captures can be stored inside [`docs/screenshots/`](docs/screenshots/) to provide visual previews on GitHub. 

*(Note: Live image files are currently placeholders to maintain a lightweight repository clone size. Capture your own test runs using the standard demonstration paths below):*

| View | Target Placeholder Path | Planned Demonstration Capture |
| :--- | :--- | :--- |
| **SOC Dashboard** | `docs/screenshots/dashboard.png` *(placeholder)* | Live command center with telemetry charts and incident feed |
| **Simulation Lab** | `docs/screenshots/simulation_lab.png` *(placeholder)* | Interactive workbench executing Test C ransomware simulation |
| **Incident Detail** | `docs/screenshots/incident_detail.png` *(placeholder)* | Forensic triage view with signal timeline and response actions |
| **Endpoints Fleet** | `docs/screenshots/endpoints.png` *(placeholder)* | Multi-host inventory with isolation toggles |
| **Model Center** | `docs/screenshots/model_center.png` *(placeholder)* | ONNX architecture parameters and confusion matrix |

---

## 26. Research & Engineering Value

1. **Dynamic Behavioral Detection:** Overcomes static signature evasion by analyzing filesystem behavioral invariants.
2. **Temporal Sequence Modeling:** Demonstrates practical application of recurrent neural networks (LSTM) to cybersecurity time-series telemetry.
3. **Hybrid Decision Architecture:** Combines deep learning pattern recognition with deterministic heuristic safety bounds to reduce false positives.
4. **Production Inference Optimization:** Deploys deep learning via ONNX Runtime, eliminating Python overhead and heavyweight framework dependencies at runtime.
5. **Session-Level Incident Deduplication:** Solves alert fatigue by aggregating high-velocity telemetry streams into unified incident entities.
6. **Safe Cyber-Physical Containment:** Employs defensive simulation that exercises containment workflows without endangering host systems.
7. **Heartbeat-Preserving Network Isolation:** Maintains agent command-and-control connectivity during host isolation.
8. **Explainable AI for SOC Operations:** Exposes granular Shannon entropy deltas, velocity metrics, and model explanations directly to analysts.
9. **Full-Duplex Asynchronous Architecture:** Integrates WebSockets with FastAPI background tasks for sub-second dashboard updates.
10. **Reproducible Test Engineering:** Includes reproducible regression scenarios (Tests A, B, and C) for validation and defense evaluation.

---

## 27. Limitations

Transparent engineering requires acknowledging current boundaries:
* **Controlled Synthetic Data:** The model was trained and evaluated on synthetic filesystem sessions. While synthetic data accurately mirrors known ransomware behavioral patterns, real-world enterprise environments exhibit significantly higher entropy diversity and varied file mutation patterns.
* **Single-Node Laboratory Environment:** Telemetry and containment were evaluated within a single Windows/Linux host environment. Enterprise multi-subnet distributed deployments require external network firewalls and directory integration.
* **Heuristic Weighting:** The behavioral scoring weights were empirically tuned against the simulation test suite and should be calibrated against specific production baseline telemetry.
* **Agent Sensor Reliance:** Detection relies on the filesystem monitoring fidelity of the underlying agent. Kernel-level rootkits operating beneath user-space filesystem drivers would require kernel driver telemetry (e.g., Windows Minifilter or Linux eBPF).

---

## 28. Future Roadmap

- [ ] **eBPF & Minifilter Sensor Drivers:** Low-level kernel driver telemetry capture for anti-tamper monitoring.
- [ ] **Pre-Encryption Early Warning Detection:** Detecting ransomware staging, shadow copy deletion (`vssadmin delete shadows`), and reconnaissance before encryption begins.
- [ ] **Attack Graph Correlation:** Graph-based correlation tracing parent-child process lineages back to initial ingress vectors.
- [ ] **Counterfactual Risk Simulation:** What-if analysis allowing analysts to model threat propagation under varying network isolation rules.
- [ ] **Automated Shadow Copy & Volume Recovery:** Automated rollback of quarantined files from Volume Shadow Copies or local snapshots upon successful containment.
- [ ] **Adversarial Robustness Testing:** Evaluating detection resilience against slow-and-low encryption evasion attacks.
- [ ] **Model Drift & Continuous Learning Pipeline:** Automated retraining triggered when incoming telemetry diverges from baseline distributions.

---

## 29. Contributing

Contributions are welcome from cybersecurity researchers, students, and software engineers:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/enhanced-telemetry`
3. Commit your changes: `git commit -m "feat: add Shannon entropy optimization"`
4. Run tests to ensure regression parity: `pytest backend/tests`
5. Push to your branch: `git push origin feature/enhanced-telemetry`
6. Open a Pull Request with a clear description of your changes and test results.

---

## 30. License

License: Not yet specified. *(Please refer to project maintainer before commercial use).*

---

## 31. Acknowledgements

RansomGuard is built upon exceptional open-source software:
* [PyTorch](https://pytorch.org/) & [ONNX Runtime](https://onnxruntime.ai/) for deep learning and high-performance inference.
* [FastAPI](https://fastapi.tiangolo.com/) & [Uvicorn](https://www.uvicorn.org/) for asynchronous backend services.
* [React](https://react.dev/), [Tailwind CSS](https://tailwindcss.com/), & [Recharts](https://recharts.org/) for the SOC dashboard interface.
* [SQLAlchemy](https://www.sqlalchemy.org/) & [SQLite](https://www.sqlite.org/) for reliable data persistence.
* [Watchdog](https://github.com/gorakhargosh/watchdog) for cross-platform filesystem event handling.
* [Lucide Icons](https://lucide.dev/) for SOC iconography.
