from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import asyncio
import os
import random
import math
import logging
from datetime import datetime
from typing import List

from app.core.database import SessionLocal, get_db
from app.schemas.simulation import SimulationStartRequest, SimulationStatusResponse
from app.schemas.telemetry import TelemetryBatchIngestRequest, TelemetryEventSchema
from app.api.telemetry import process_telemetry_batch
from app.security.rbac import get_current_user, require_role
from app.models.user import User
from app.core.websocket_manager import ws_manager

router = APIRouter()
logger = logging.getLogger(__name__)

SIMULATION_STATE = {
    "is_running": False,
    "simulation_id": "none",
    "simulation_type": "combined",
    "target_hostname": "demo-soc-endpoint-vm01",
    "files_touched": 0,
    "files_modified": 0,
    "current_rate": 0.0,
    "entropy_change": 0.0,
    "ml_probability": 0.0,
    "behavioral_score": 0.0,
    "threat_score": 0.0,
    "detection_status": "NORMAL",
    "containment_status": "MONITORING"
}

def calculate_shannon_entropy_bytes(data: bytes) -> float:
    if not data:
        return 0.0
    byte_counts = [0] * 256
    for b in data:
        byte_counts[b] += 1
    entropy = 0.0
    total = len(data)
    for count in byte_counts:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return round(entropy, 4)

async def run_simulation_task(request: SimulationStartRequest):
    global SIMULATION_STATE
    sim_id = f"SIM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}"
    SIMULATION_STATE["is_running"] = True
    SIMULATION_STATE["simulation_id"] = sim_id
    SIMULATION_STATE["simulation_type"] = request.simulation_type
    SIMULATION_STATE["files_touched"] = 0
    SIMULATION_STATE["files_modified"] = 0
    SIMULATION_STATE["ml_probability"] = 0.0
    SIMULATION_STATE["behavioral_score"] = 0.0
    SIMULATION_STATE["threat_score"] = 0.0
    SIMULATION_STATE["detection_status"] = "NORMAL"
    SIMULATION_STATE["containment_status"] = "MONITORING"

    lab_dir = os.getenv("SIMULATION_DIRECTORY", "./scratch/ransim_lab")
    os.makedirs(lab_dir, exist_ok=True)

    total_files = request.number_of_files
    interval = 1.0 / max(1.0, request.modification_rate)

    sim_type = request.simulation_type.lower()
    if sim_type == "rapid_modification":
        proc_name = request.process_name or "rapid_worker.exe"
        is_suspicious_proc = 0
        do_encryption = False
        do_ext_change = False
    elif sim_type == "entropy_increase":
        proc_name = request.process_name or "ransim_entropy.exe"
        is_suspicious_proc = 1
        do_encryption = True
        do_ext_change = False
    elif sim_type == "extension_change":
        proc_name = request.process_name or "ransim_extension.exe"
        is_suspicious_proc = 1
        do_encryption = False
        do_ext_change = True
    else:  # combined
        proc_name = request.process_name or "ransim_combined.exe"
        is_suspicious_proc = 1
        do_encryption = True
        do_ext_change = request.extension_changes

    logger.info(f"[Simulation Lab] Starting safe simulation ({sim_type}) in '{lab_dir}' ({total_files} files, {request.modification_rate} ops/s)...")

    db = SessionLocal()
    try:
        from app.models.endpoint import Endpoint
        target_host = request.target_hostname
        if not target_host:
            online_ep = db.query(Endpoint).filter(Endpoint.status == "online").first()
            target_host = online_ep.hostname if online_ep else "demo-soc-endpoint-vm01"

        for i in range(total_files):
            if not SIMULATION_STATE["is_running"]:
                break

            events: List[TelemetryEventSchema] = []
            file_name = f"safe_lab_doc_{i:03d}.docx"
            file_path = os.path.join(lab_dir, file_name)

            # 1. Create file with initial benign content
            benign_content = ("Initial safe contents for simulation testing.\n" * 8).encode("utf-8")
            with open(file_path, "wb") as f:
                f.write(benign_content)

            benign_entropy = calculate_shannon_entropy_bytes(benign_content)
            SIMULATION_STATE["files_touched"] += 1

            create_event = TelemetryEventSchema(
                file_path=file_path,
                operation="create",
                file_size=float(len(benign_content)),
                entropy=benign_entropy,
                entropy_change=0.0,
                mod_rate=round(interval, 3),
                ext_changed=0,
                is_suspicious_process=is_suspicious_proc,
                file_path_length=len(file_path),
                is_common_extension=1,
                process_name=proc_name
            )
            events.append(create_event)

            await asyncio.sleep(interval)

            # 2. Modify file according to simulation pattern
            modify_threshold = total_files * 0.2
            if i >= modify_threshold:
                if do_ext_change:
                    new_path = file_path.replace(".docx", ".encrypted")
                else:
                    new_path = file_path

                if do_encryption:
                    # High Shannon entropy payload (> 7.5)
                    mod_bytes = bytes([random.randint(0, 255) for _ in range(2048)])
                else:
                    # Normal benign content (low/moderate entropy)
                    mod_bytes = ("Updated normal benign document content with low entropy.\n" * 12).encode("utf-8")

                with open(new_path, "wb") as f:
                    f.write(mod_bytes)

                if do_ext_change and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass

                mod_entropy = calculate_shannon_entropy_bytes(mod_bytes)
                entropy_diff = round(mod_entropy - benign_entropy, 4)

                modify_event = TelemetryEventSchema(
                    file_path=new_path,
                    operation="modify",
                    file_size=float(len(mod_bytes)),
                    entropy=mod_entropy,
                    entropy_change=entropy_diff,
                    mod_rate=round(interval, 3),
                    ext_changed=1 if do_ext_change else 0,
                    is_suspicious_process=is_suspicious_proc,
                    file_path_length=len(new_path),
                    is_common_extension=0 if do_ext_change else 1,
                    process_name=proc_name
                )
                events.append(modify_event)
                SIMULATION_STATE["files_modified"] += 1
                SIMULATION_STATE["entropy_change"] = entropy_diff

            # 3. Process events through real Backend Telemetry -> ONNX Inference -> Risk Engine -> Incident DB Pipeline
            batch = TelemetryBatchIngestRequest(
                hostname=target_host,
                events=events,
                simulation_id=sim_id,
                reset_buffer=(i == 0)
            )
            pipeline_result = await process_telemetry_batch(batch, db)
            real_risk = pipeline_result["endpoint_risk"]
            real_ml_prob = pipeline_result.get("ml_probability", 0.0)
            real_behavioral = pipeline_result.get("behavioral_score", 0.0)

            # Update Simulation State with REAL backend scores
            SIMULATION_STATE["current_rate"] = round(1.0 / max(0.01, interval), 1)
            SIMULATION_STATE["ml_probability"] = real_ml_prob
            SIMULATION_STATE["behavioral_score"] = real_behavioral
            SIMULATION_STATE["threat_score"] = real_risk

            if real_risk < 30.0:
                SIMULATION_STATE["detection_status"] = "NORMAL"
            elif real_risk < 60.0:
                SIMULATION_STATE["detection_status"] = "SUSPICIOUS"
            elif real_risk < 80.0:
                SIMULATION_STATE["detection_status"] = "HIGH RISK"
            else:
                SIMULATION_STATE["detection_status"] = "RANSOMWARE DETECTED"

            if real_risk >= 90.0:
                SIMULATION_STATE["containment_status"] = "CONTAINED (Process Terminated & Endpoint Isolated)"
            else:
                SIMULATION_STATE["containment_status"] = "MONITORING"

                # Safe Containment: Clean up encrypted test files strictly inside scratch/ransim_lab/
                try:
                    for f_item in os.listdir(lab_dir):
                        if f_item.endswith(".encrypted"):
                            os.remove(os.path.join(lab_dir, f_item))
                except Exception as ce:
                    logger.warning(f"[Simulation Lab] Sandbox cleanup notice: {ce}")

            # 4. Broadcast live Simulation Progress over WebSocket
            await ws_manager.broadcast({
                "type": "SIMULATION_PROGRESS",
                "data": SIMULATION_STATE
            })

    except Exception as e:
        logger.error(f"[Simulation Lab] Simulation task error: {e}", exc_info=True)
    finally:
        db.close()

    SIMULATION_STATE["is_running"] = False
    await ws_manager.broadcast({
        "type": "SIMULATION_COMPLETED",
        "data": SIMULATION_STATE
    })
    logger.info(f"[Simulation Lab] Simulation completed. Final threat score: {SIMULATION_STATE['threat_score']:.1f}%")

@router.post("/start", response_model=SimulationStatusResponse)
async def start_simulation(
    request: SimulationStartRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_role(["admin", "soc_analyst"]))
):
    if SIMULATION_STATE["is_running"]:
        raise HTTPException(status_code=400, detail="A simulation is already in progress.")

    background_tasks.add_task(run_simulation_task, request)
    return SIMULATION_STATE

@router.post("/stop", response_model=SimulationStatusResponse)
async def stop_simulation(
    current_user: User = Depends(require_role(["admin", "soc_analyst"]))
):
    global SIMULATION_STATE
    SIMULATION_STATE["is_running"] = False
    SIMULATION_STATE["detection_status"] = "STOPPED BY USER"
    SIMULATION_STATE["containment_status"] = "MANUAL_STOP"
    return SIMULATION_STATE

@router.get("/status", response_model=SimulationStatusResponse)
async def get_simulation_status():
    return SIMULATION_STATE
