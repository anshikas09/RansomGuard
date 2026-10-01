from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    file_path = Column(Text, nullable=False)
    operation = Column(String, nullable=False)  # create, modify, delete, rename
    file_size = Column(Float, default=0.0)
    entropy = Column(Float, default=0.0)
    entropy_change = Column(Float, default=0.0)
    mod_rate = Column(Float, default=0.0)
    ext_changed = Column(Integer, default=0)
    is_suspicious_process = Column(Integer, default=0)
    file_path_length = Column(Integer, default=0)
    is_common_extension = Column(Integer, default=1)
    ransomware_probability = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    severity = Column(String, default="LOW")
    process_name = Column(String, nullable=True)
    
    endpoint = relationship("Endpoint", back_populates="telemetry")
