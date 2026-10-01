from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class IncidentResponse(BaseModel):
    id: int
    endpoint_id: int
    timestamp: datetime
    threat_score: float
    confidence: Optional[str]
    severity: str
    suspected_process: Optional[str]
    affected_files: List[str] = []
    behavior_timeline: List[Dict[str, Any]] = []
    model_explanation: Optional[str]
    detection_signals: List[Dict[str, Any]] = []
    containment_status: str
    response_actions: List[Dict[str, Any]] = []
    analyst_notes: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

class IncidentUpdateRequest(BaseModel):
    status: Optional[str] = None
    analyst_notes: Optional[str] = None
    containment_action: Optional[str] = None
