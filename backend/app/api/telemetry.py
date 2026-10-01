from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import numpy as np
import logging

from app.core.database import get_db
from app.models.endpoint import Endpoint
from app.models.telemetry import TelemetryEvent
from app.models.incident import Incident, Threat, ContainmentAction
from app.models.audit_log import AuditLog
from app.schemas.telemetry import TelemetryBatchIngestRequest, TelemetryEventResponse, TelemetryEventSchema
from app.ml.onnx_runner import inference_engine
from app.incidents.risk_engine import calculate_risk_score
from app.core.websocket_manager import ws_manager

router = APIRouter()
logger = logging.getLogger(__name__)

# Buffer for rolling sequence window per endpoint
ENDPOINT_BUFFERS: Dict[int, List[List[float]]] = {}

async def process_telemetry_batch(
    batch: TelemetryBatchIngestRequest,
    db: Session
) -> Dict[str, Any]:
    """
    Core detection pipeline processing telemetry events through:
    Feature Vector -> 10-Event Sequence -> ONNX Inference -> Risk Engine -> Incident DB -> Containment -> WS Broadcast
    """
    endpoint = db.query(Endpoint).filter(Endpoint.hostname == batch.hostname).first()
    if not endpoint:
        endpoint = Endpoint(
            hostname=batch.hostname,
            os="Windows Security Host",
            ip_address="127.0.0.1",
            agent_version="1.0.0",
            status="online",
            telemetry_status="active"
        )
        db.add(endpoint)
        db.commit()
        db.refresh(endpoint)

    if endpoint.id not in ENDPOINT_BUFFERS:
        ENDPOINT_BUFFERS[endpoint.id] = []

    if batch.reset_buffer:
        ENDPOINT_BUFFERS[endpoint.id] = []
        logger.info(f"[Telemetry Buffer] Rolling buffer reset for endpoint #{endpoint.id} ({endpoint.hostname})")

    ingested_events = []
    max_risk = 0.0
    max_ml_prob = 0.0
    max_behavioral = 0.0
    highest_severity = "LOW"
    suspected_proc = None
    affected_files = []
    detection_signals = []

    for event_data in batch.events:
        # 1. Feature Extraction Vector (8 features):
        # [file_size, entropy, entropy_change, mod_rate, ext_changed, is_suspicious_process, file_path_length, is_common_extension]
        feature_vec = [
            float(event_data.file_size),
            float(event_data.entropy),
            float(event_data.entropy_change),
            float(event_data.mod_rate),
            float(event_data.ext_changed),
            float(event_data.is_suspicious_process),
            float(event_data.file_path_length),
            float(event_data.is_common_extension)
        ]

        # 2. Maintain rolling 10-event sequence buffer
        buf = ENDPOINT_BUFFERS[endpoint.id]
        buf.append(feature_vec)
        if len(buf) > 10:
            buf.pop(0)

        # Pad to shape (10, 8) if less than 10 events
        if len(buf) < 10:
            pad = [[0.0] * 8] * (10 - len(buf))
            seq_matrix = np.array(pad + buf, dtype=np.float32)
        else:
            seq_matrix = np.array(buf, dtype=np.float32)

        # 3. ONNX Model Inference
        ml_prob = inference_engine.predict(seq_matrix)
        logger.info(f"[ONNX Inference] Input sequence shape: {seq_matrix.shape} -> Predicted ML probability: {ml_prob:.4f}")

        # 4. Risk Engine Evaluation
        risk_score, severity, action, behavioral_score = calculate_risk_score(
            ml_probability=ml_prob,
            event_frequency=1.0 / max(0.01, event_data.mod_rate),
            entropy_change=event_data.entropy_change,
            ext_changes=event_data.ext_changed,
            process_signals=event_data.is_suspicious_process,
            return_details=True
        )
        logger.info(f"[Risk Engine] ML Prob: {ml_prob*100.0:.1f}% | Behavioral: {behavioral_score:.1f}% | Risk: {risk_score:.1f}% | Severity: {severity}")

        if ml_prob > max_ml_prob:
            max_ml_prob = ml_prob
        if behavioral_score > max_behavioral:
            max_behavioral = behavioral_score

        # 5. Store Telemetry Event Record in DB
        db_event = TelemetryEvent(
            endpoint_id=endpoint.id,
            timestamp=datetime.utcnow(),
            file_path=event_data.file_path,
            operation=event_data.operation,
            file_size=event_data.file_size,
            entropy=event_data.entropy,
            entropy_change=event_data.entropy_change,
            mod_rate=event_data.mod_rate,
            ext_changed=event_data.ext_changed,
            is_suspicious_process=event_data.is_suspicious_process,
            file_path_length=event_data.file_path_length,
            is_common_extension=event_data.is_common_extension,
            ransomware_probability=ml_prob,
            risk_score=risk_score,
            severity=severity,
            process_name=event_data.process_name
        )
        db.add(db_event)
        ingested_events.append(db_event)

        if risk_score > max_risk:
            max_risk = risk_score
            highest_severity = severity
            suspected_proc = event_data.process_name or "unknown_process"

        if event_data.file_path not in affected_files:
            affected_files.append(event_data.file_path)

        if event_data.entropy > 7.0:
            detection_signals.append({"signal": "High Shannon Entropy (>7.0)", "value": round(event_data.entropy, 2)})
        if event_data.ext_changed == 1:
            detection_signals.append({"signal": "Rapid File Extension Change (.encrypted)", "file": event_data.file_path})
        if event_data.is_suspicious_process == 1:
            detection_signals.append({"signal": "Unverified/Suspicious Process Execution", "process": event_data.process_name})

    endpoint.current_risk = max_risk
    endpoint.last_heartbeat = datetime.utcnow()
    endpoint.telemetry_status = "active"

    # 6. Create or Update Incident Record in Database if risk threshold (80.0%) crossed
    created_incident = None
    if max_risk >= 80.0:
        recent_incident = None
        # Step A: Consolidate by simulation_id if present
        if batch.simulation_id:
            candidates = db.query(Incident).filter(
                Incident.endpoint_id == endpoint.id,
                Incident.status != "resolved"
            ).order_by(Incident.id.desc()).limit(10).all()
            for cand in candidates:
                signals = cand.detection_signals or []
                if any(isinstance(s, dict) and s.get("simulation_id") == batch.simulation_id for s in signals):
                    recent_incident = cand
                    break

        # Step B: Fall back to ongoing attack window (300s) for matching endpoint and process
        if not recent_incident:
            cand = db.query(Incident).filter(
                Incident.endpoint_id == endpoint.id,
                Incident.status != "resolved"
            ).order_by(Incident.id.desc()).first()
            if cand:
                ref_time = cand.updated_at or cand.timestamp
                if (datetime.utcnow() - ref_time).total_seconds() < 300:
                    if not cand.suspected_process or cand.suspected_process == suspected_proc or not suspected_proc:
                        recent_incident = cand

        if recent_incident:
            created_incident = recent_incident
            created_incident.updated_at = datetime.utcnow()
            if max_risk > created_incident.threat_score:
                created_incident.threat_score = max_risk
                created_incident.severity = highest_severity
            existing_files = set(created_incident.affected_files or [])
            for f in affected_files[:20]:
                existing_files.add(f)
            created_incident.affected_files = list(existing_files)
        else:
            if batch.simulation_id:
                detection_signals.append({"signal": "Simulation ID", "simulation_id": batch.simulation_id})

            created_incident = Incident(
                endpoint_id=endpoint.id,
                timestamp=datetime.utcnow(),
                threat_score=max_risk,
                confidence="high" if max_risk > 90.0 else "medium",
                severity=highest_severity,
                suspected_process=suspected_proc or "unknown_process",
                affected_files=affected_files[:20],
                behavior_timeline=[
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": f"Automated ONNX LSTM detection triggered with threat score {max_risk:.1f}%",
                        "severity": highest_severity
                    }
                ],
                model_explanation=f"ONNX LSTM Sequence Model observed rapid file mutation and high entropy pattern with probability {max_risk/100.0:.3f}",
                detection_signals=detection_signals[:10],
                containment_status="none",
                status="new"
            )
            db.add(created_incident)
            db.flush()

        endpoint.last_threat_id = created_incident.id
        logger.info(f"[Incident Engine] Incident ID #{created_incident.id} updated/created in DB for Endpoint #{endpoint.id} (Threat Score: {max_risk:.1f}%)")

        # 7. Execute Automated Containment if containment threshold (90.0%) crossed
        if max_risk >= 90.0:
            endpoint.is_isolated = True
            if created_incident.containment_status != "completed":
                created_incident.containment_status = "completed"
                created_incident.status = "contained"
                created_incident.response_actions = [
                    {"action": "kill_process", "process": suspected_proc, "status": "success"},
                    {"action": "isolate_endpoint", "status": "success"},
                    {"action": "quarantine_sandbox_files", "status": "success"}
                ]

                contain_action = ContainmentAction(
                    incident_id=created_incident.id,
                    endpoint_id=endpoint.id,
                    action_type="kill_process",
                    action_status="executed",
                    executed_at=datetime.utcnow(),
                    result={"process_killed": suspected_proc, "network_isolated": True, "sandbox_quarantined": True}
                )
                db.add(contain_action)

                audit = AuditLog(
                    action="AUTOMATED_CONTAINMENT_EXECUTED",
                    endpoint_id=endpoint.id,
                    incident_id=created_incident.id,
                    result="success",
                    details={"threat_score": max_risk, "process": suspected_proc, "isolated": True}
                )
                db.add(audit)
                logger.info(f"[Containment Engine] Automated containment executed for Incident #{created_incident.id} on Endpoint #{endpoint.id}")

    db.commit()

    # 8. Broadcast Real-Time WebSocket Notification
    await ws_manager.broadcast({
        "type": "TELEMETRY_BATCH_INGESTED",
        "data": {
            "endpoint_id": endpoint.id,
            "hostname": endpoint.hostname,
            "max_risk": max_risk,
            "severity": highest_severity,
            "events_count": len(batch.events),
            "incident_created": created_incident.id if created_incident else None
        }
    })

    if created_incident:
        await ws_manager.broadcast({
            "type": "INCIDENT_UPDATED",
            "data": {
                "incident_id": created_incident.id,
                "endpoint_id": endpoint.id,
                "threat_score": max_risk,
                "severity": highest_severity,
                "containment_status": created_incident.containment_status
            }
        })

    return {
        "status": "success",
        "ingested_count": len(ingested_events),
        "endpoint_risk": max_risk,
        "ml_probability": round(max_ml_prob * 100.0, 1),
        "behavioral_score": round(max_behavioral, 1),
        "incident_id": created_incident.id if created_incident else None,
        "created_incident": created_incident,
        "endpoint": endpoint
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def ingest_telemetry(
    batch: TelemetryBatchIngestRequest,
    db: Session = Depends(get_db)
):
    res = await process_telemetry_batch(batch, db)
    return {
        "status": "success",
        "ingested_count": res["ingested_count"],
        "endpoint_risk": res["endpoint_risk"],
        "incident_id": res["incident_id"]
    }

@router.get("/recent", response_model=List[TelemetryEventResponse])
async def get_recent_telemetry(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return db.query(TelemetryEvent).order_by(TelemetryEvent.timestamp.desc()).limit(limit).all()

@router.get("/stats")
async def get_telemetry_stats(
    db: Session = Depends(get_db)
):
    total_events = db.query(TelemetryEvent).count()
    return {
        "total_events": total_events
    }
