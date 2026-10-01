from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Endpoint(Base):
    __tablename__ = "endpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, nullable=False, index=True)
    os = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    agent_version = Column(String, nullable=True)
    status = Column(String, default="offline")  # online, offline
    last_heartbeat = Column(DateTime, nullable=True)
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    current_risk = Column(Float, default=0.0)
    last_threat_id = Column(Integer, nullable=True)
    telemetry_status = Column(String, default="disconnected")
    is_isolated = Column(Boolean, default=False)
    monitoring_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    heartbeats = relationship("EndpointHeartbeat", back_populates="endpoint", cascade="all, delete-orphan")
    telemetry = relationship("TelemetryEvent", back_populates="endpoint", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="endpoint", cascade="all, delete-orphan")

class EndpointHeartbeat(Base):
    __tablename__ = "endpoint_heartbeats"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    telemetry_count = Column(Integer, default=0)
    status = Column(String, default="online")
    
    endpoint = relationship("Endpoint", back_populates="heartbeats")
