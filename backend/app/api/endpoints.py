from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.endpoint import Endpoint, EndpointHeartbeat
from app.models.audit_log import AuditLog
from app.schemas.endpoint import (
    EndpointRegisterRequest,
    EndpointHeartbeatRequest,
    EndpointResponse,
    IsolationRequest
)
from app.security.rbac import get_current_user, require_role
from app.models.user import User
from app.core.websocket_manager import ws_manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=EndpointResponse)
async def register_endpoint(
    request: EndpointRegisterRequest,
    db: Session = Depends(get_db)
):
    endpoint = db.query(Endpoint).filter(Endpoint.hostname == request.hostname).first()
    if not endpoint:
        endpoint = Endpoint(
            hostname=request.hostname,
            os=request.os,
            ip_address=request.ip_address,
            agent_version=request.agent_version,
            status="online",
            last_heartbeat=datetime.utcnow(),
            telemetry_status="connected",
            monitoring_enabled=True
        )
        db.add(endpoint)
    else:
        endpoint.os = request.os
        endpoint.ip_address = request.ip_address
        endpoint.agent_version = request.agent_version
        endpoint.status = "online"
        endpoint.last_heartbeat = datetime.utcnow()
        endpoint.telemetry_status = "connected"

    db.commit()
    db.refresh(endpoint)

    await ws_manager.broadcast({
        "type": "ENDPOINT_UPDATED",
        "data": {
            "id": endpoint.id,
            "hostname": endpoint.hostname,
            "status": endpoint.status
        }
    })

    return endpoint

@router.post("/heartbeat")
async def endpoint_heartbeat(
    request: EndpointHeartbeatRequest,
    db: Session = Depends(get_db)
):
    endpoint = db.query(Endpoint).filter(Endpoint.hostname == request.hostname).first()
    if not endpoint:
        endpoint = Endpoint(
            hostname=request.hostname,
            status="online",
            telemetry_status="connected"
        )
        db.add(endpoint)
        db.commit()
        db.refresh(endpoint)

    endpoint.status = request.status
    endpoint.last_heartbeat = datetime.utcnow()
    endpoint.cpu_usage = request.cpu_usage
    endpoint.memory_usage = request.memory_usage
    endpoint.telemetry_status = "connected"

    heartbeat_log = EndpointHeartbeat(
        endpoint_id=endpoint.id,
        timestamp=datetime.utcnow(),
        cpu_usage=request.cpu_usage,
        memory_usage=request.memory_usage,
        telemetry_count=request.telemetry_count,
        status=request.status
    )
    db.add(heartbeat_log)
    db.commit()

    return {"status": "heartbeat_received", "endpoint_id": endpoint.id}

@router.get("/", response_model=List[EndpointResponse])
async def list_endpoints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Endpoint).all()

@router.get("/{endpoint_id}", response_model=EndpointResponse)
async def get_endpoint(
    endpoint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return endpoint

@router.post("/{endpoint_id}/isolate")
async def toggle_endpoint_isolation(
    endpoint_id: int,
    request: IsolationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "soc_analyst"]))
):
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    is_isolate = request.action.lower() == "isolate"
    endpoint.is_isolated = is_isolate
    
    audit = AuditLog(
        user_id=current_user.id,
        action="ENDPOINT_ISOLATION_TOGGLED",
        endpoint_id=endpoint.id,
        result="success",
        details={"action": request.action, "reason": request.reason}
    )
    db.add(audit)
    db.commit()

    await ws_manager.broadcast({
        "type": "CONTAINMENT_TRIGGERED",
        "data": {
            "endpoint_id": endpoint.id,
            "hostname": endpoint.hostname,
            "action": request.action,
            "is_isolated": is_isolate
        }
    })

    return {
        "message": f"Endpoint {endpoint.hostname} {'isolated' if is_isolate else 'released'} successfully.",
        "is_isolated": is_isolate
    }

@router.delete("/{endpoint_id}")
async def delete_endpoint(
    endpoint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "soc_analyst"]))
):
    endpoint = db.query(Endpoint).filter(Endpoint.id == endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    hostname = endpoint.hostname
    db.delete(endpoint)
    audit = AuditLog(
        user_id=current_user.id,
        action="ENDPOINT_DELETED",
        endpoint_id=endpoint_id,
        result="success",
        details={"hostname": hostname}
    )
    db.add(audit)
    db.commit()

    await ws_manager.broadcast({
        "type": "ENDPOINT_DELETED",
        "data": {
            "id": endpoint_id,
            "hostname": hostname
        }
    })

    return {"message": f"Endpoint {hostname} deleted successfully"}
