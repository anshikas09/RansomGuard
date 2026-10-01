from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    endpoint_id = Column(Integer, nullable=True)
    incident_id = Column(Integer, nullable=True)
    result = Column(String, nullable=False, default="success")  # success, failure
    details = Column(JSON, default=dict)
    
    user = relationship("User", back_populates="audit_logs")
