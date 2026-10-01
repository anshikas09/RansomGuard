from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TelemetryEventSchema(BaseModel):
    file_path: str
    operation: str
    file_size: float = 0.0
    entropy: float = 0.0
    entropy_change: float = 0.0
    mod_rate: float = 0.0
    ext_changed: int = 0
    is_suspicious_process: int = 0
    file_path_length: int = 0
    is_common_extension: int = 1
    process_name: Optional[str] = "unknown"

class TelemetryBatchIngestRequest(BaseModel):
    hostname: str
    events: List[TelemetryEventSchema]
    simulation_id: Optional[str] = None
    reset_buffer: Optional[bool] = False

class TelemetryEventResponse(TelemetryEventSchema):
    id: int
    endpoint_id: int
    timestamp: datetime
    ransomware_probability: Optional[float] = 0.0
    risk_score: Optional[float] = 0.0
    severity: Optional[str] = "LOW"
