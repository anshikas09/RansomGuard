from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.incident import Incident, ContainmentAction
from app.models.audit_log import AuditLog
from app.schemas.incident import IncidentResponse, IncidentUpdateRequest
from app.security.rbac import get_current_user, require_role
from app.models.user import User
from app.core.websocket_manager import ws_manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[IncidentResponse])
async def list_incidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Incident).order_by(Incident.timestamp.desc()).all()

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    request: IncidentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "soc_analyst"]))
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if request.status:
        incident.status = request.status

    if request.analyst_notes is not None:
        incident.analyst_notes = request.analyst_notes

    if request.containment_action:
        incident.containment_status = "completed"
        actions = incident.response_actions or []
        actions.append({
            "action": request.containment_action,
            "executed_by": current_user.email,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
        })
        incident.response_actions = actions

        contain_record = ContainmentAction(
            incident_id=incident.id,
            endpoint_id=incident.endpoint_id,
            action_type=request.containment_action,
            action_status="executed",
            executed_at=datetime.utcnow(),
            executed_by=current_user.id,
            result={"manual_override": True}
        )
        db.add(contain_record)

    incident.updated_at = datetime.utcnow()

    audit = AuditLog(
        user_id=current_user.id,
        action="INCIDENT_UPDATED",
        incident_id=incident.id,
        result="success",
        details={"status": incident.status, "notes_added": bool(request.analyst_notes)}
    )
    db.add(audit)
    db.commit()
    db.refresh(incident)

    await ws_manager.broadcast({
        "type": "INCIDENT_UPDATED",
        "data": {
            "incident_id": incident.id,
            "status": incident.status,
            "containment_status": incident.containment_status
        }
    })

    return incident
