from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    threat_score = Column(Float, nullable=False, index=True)
    confidence = Column(String, default="high")  # low, medium, high
    severity = Column(String, nullable=False)  # low, medium, high, critical
    suspected_process = Column(String, nullable=True)
    affected_files = Column(JSON, default=list)
    behavior_timeline = Column(JSON, default=list)
    model_explanation = Column(Text, nullable=True)
    detection_signals = Column(JSON, default=list)
    containment_status = Column(String, default="none")  # none, triggered, completed, failed
    response_actions = Column(JSON, default=list)
    analyst_notes = Column(Text, nullable=True)
    status = Column(String, default="new")  # new, investigating, contained, resolved, false_positive
    model_version_id = Column(Integer, ForeignKey("model_versions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    endpoint = relationship("Endpoint", back_populates="incidents")
    threats = relationship("Threat", back_populates="incident", cascade="all, delete-orphan")
    containment_actions = relationship("ContainmentAction", back_populates="incident", cascade="all, delete-orphan")
    model_version = relationship("ModelVersion", back_populates="incidents")
    alerts = relationship("Alert", back_populates="incident", cascade="all, delete-orphan")

class Threat(Base):
    __tablename__ = "threats"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    threat_score = Column(Float, nullable=False)
    file_path = Column(Text, nullable=False)
    process_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    
    incident = relationship("Incident", back_populates="threats")

class ContainmentAction(Base):
    __tablename__ = "containment_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String, nullable=False)  # kill_process, isolate_endpoint, quarantine_files
    action_status = Column(String, default="pending")  # pending, executed, failed
    executed_at = Column(DateTime, default=datetime.utcnow)
    executed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    result = Column(JSON, default=dict)
    
    incident = relationship("Incident", back_populates="containment_actions")
    endpoint = relationship("Endpoint")
