from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class ModelVersionResponse(BaseModel):
    id: int
    version: str
    framework: str
    input_features: List[str]
    sequence_length: int
    training_status: str
    last_trained_at: Optional[datetime]
    deployment_status: str
    metrics: Dict[str, Any]
    created_at: datetime

class TrainModelRequest(BaseModel):
    num_benign_sessions: int = 100
    num_malicious_sessions: int = 50
    events_per_session: int = 50
    epochs: int = 30
