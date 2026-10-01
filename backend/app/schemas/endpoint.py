from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EndpointRegisterRequest(BaseModel):
    hostname: str
    os: Optional[str] = "Windows 11 Security Lab"
    ip_address: Optional[str] = "127.0.0.1"
    agent_version: Optional[str] = "1.0.0"

class EndpointHeartbeatRequest(BaseModel):
    hostname: str
    cpu_usage: float
    memory_usage: float
    telemetry_count: int = 0
    status: str = "online"

class EndpointResponse(BaseModel):
    id: int
    hostname: str
    os: Optional[str]
    ip_address: Optional[str]
    agent_version: Optional[str]
    status: str
    last_heartbeat: Optional[datetime]
    cpu_usage: float
    memory_usage: float
    current_risk: float
    last_threat_id: Optional[int]
    telemetry_status: str
    is_isolated: bool
    monitoring_enabled: bool
    created_at: datetime

class IsolationRequest(BaseModel):
    action: str  # "isolate" or "release"
    reason: Optional[str] = "SOC Analyst action"
