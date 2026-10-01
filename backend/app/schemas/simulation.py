from pydantic import BaseModel
from typing import Optional

class SimulationStartRequest(BaseModel):
    simulation_type: str = "combined"  # rapid_modification, extension_change, entropy_increase, combined
    number_of_files: int = 30
    modification_rate: float = 10.0  # files/sec
    extension_changes: bool = True
    entropy_behavior: str = "linear_increase"
    duration_seconds: int = 30
    intensity: str = "medium"  # low, medium, high
    target_hostname: Optional[str] = None
    process_name: Optional[str] = None

class SimulationStatusResponse(BaseModel):
    is_running: bool
    simulation_id: Optional[str] = "none"
    simulation_type: str
    target_hostname: Optional[str] = "demo-soc-endpoint-vm01"
    files_touched: int
    files_modified: int
    current_rate: float
    entropy_change: float
    ml_probability: float = 0.0
    behavioral_score: float = 0.0
    threat_score: float = 0.0
    detection_status: str
    containment_status: str
