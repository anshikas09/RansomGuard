from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
import glob
import logging

from app.core.database import get_db
from app.models.incident import Incident, ContainmentAction, Threat
from app.models.alert import Alert
from app.models.telemetry import TelemetryEvent
from app.models.endpoint import Endpoint, EndpointHeartbeat
from app.models.audit_log import AuditLog
from app.models.chatbot import ChatbotConversation
from app.models.user import User
from app.security.rbac import require_role
from app.core.websocket_manager import ws_manager
from app.api.telemetry import ENDPOINT_BUFFERS
from app.api.simulation import SIMULATION_STATE

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/reset")
async def reset_demo_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "soc_analyst"]))
):
    """
    Safely resets local demo and simulation data only.
    Preserves: Users, Authentication, Models, Model Versions, and Endpoint Configurations.
    Clears: Incidents, Containment Actions, Threats, Alerts, Telemetry Events, and Sandbox files.
    """
    try:
        # 1. Count records before clearing for audit reporting
        incidents_count = db.query(Incident).count()
        telemetry_count = db.query(TelemetryEvent).count()
        containment_count = db.query(ContainmentAction).count()

        # 2. Delete test threats, alerts, containment actions, and incidents
        db.query(Threat).delete()
        db.query(Alert).delete()
        db.query(ContainmentAction).delete()
        db.query(Incident).delete()

        # 3. Delete telemetry events and heartbeats
        db.query(TelemetryEvent).delete()
        db.query(EndpointHeartbeat).delete()

        # 4. Clean simulation audit logs and test conversations
        db.query(ChatbotConversation).delete()
        db.query(AuditLog).filter(
            AuditLog.action.in_([
                "TELEMETRY_BATCH_INGESTED",
                "AUTOMATED_CONTAINMENT_EXECUTED",
                "ENDPOINT_ISOLATION_TOGGLED",
                "INCIDENT_UPDATED"
            ])
        ).delete(synchronize_session=False)

        # 5. Reset endpoint runtime status without deleting endpoints
        endpoints = db.query(Endpoint).all()
        for ep in endpoints:
            ep.current_risk = 0.0
            ep.is_isolated = False
            ep.last_threat_id = None
            ep.telemetry_status = "idle"
            ep.status = "online"

        db.commit()

        # 6. Flush in-memory buffers
        ENDPOINT_BUFFERS.clear()

        # 7. Reset simulation state
        SIMULATION_STATE["is_running"] = False
        SIMULATION_STATE["simulation_id"] = "none"
        SIMULATION_STATE["files_touched"] = 0
        SIMULATION_STATE["files_modified"] = 0
        SIMULATION_STATE["current_rate"] = 0.0
        SIMULATION_STATE["entropy_change"] = 0.0
        SIMULATION_STATE["ml_probability"] = 0.0
        SIMULATION_STATE["behavioral_score"] = 0.0
        SIMULATION_STATE["threat_score"] = 0.0
        SIMULATION_STATE["detection_status"] = "NORMAL"
        SIMULATION_STATE["containment_status"] = "MONITORING"

        # 8. Clean up temporary test files from simulation directory
        sim_dir = os.getenv("SIMULATION_DIRECTORY", "./scratch/ransim_lab")
        if os.path.exists(sim_dir):
            for file_path in glob.glob(os.path.join(sim_dir, "*")):
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as ex:
                    logger.warning(f"Could not remove test file {file_path}: {ex}")

        # 9. Broadcast real-time reset event over WebSockets
        await ws_manager.broadcast({
            "type": "DEMO_DATA_RESET",
            "data": {
                "message": "Local demo data reset successfully",
                "timestamp": None
            }
        })
        await ws_manager.broadcast({
            "type": "INCIDENT_UPDATED",
            "data": {}
        })
        await ws_manager.broadcast({
            "type": "TELEMETRY_BATCH_INGESTED",
            "data": {}
        })
        await ws_manager.broadcast({
            "type": "SIMULATION_PROGRESS",
            "data": SIMULATION_STATE
        })

        logger.info(f"[Demo Reset] Local demo data reset completed by {current_user.email}. Cleared {incidents_count} incidents, {telemetry_count} telemetry events.")

        return {
            "status": "success",
            "message": "Local demo and simulation data safely reset.",
            "cleared": {
                "incidents": incidents_count,
                "telemetry_events": telemetry_count,
                "containment_actions": containment_count,
                "endpoints_reset": len(endpoints)
            }
        }

    except Exception as e:
        db.rollback()
        logger.error(f"[Demo Reset] Error during demo data reset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset demo data: {str(e)}"
        )
