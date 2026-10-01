from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, nullable=False, unique=True)
    framework = Column(String, default="pytorch_onnx")
    input_features = Column(JSON, default=list)
    sequence_length = Column(Integer, default=10)
    training_status = Column(String, default="not_trained")  # not_trained, training, completed, failed
    last_trained_at = Column(DateTime, nullable=True)
    deployment_status = Column(String, default="inactive")  # inactive, active
    metrics = Column(JSON, default=dict)
    onnx_path = Column(String, nullable=True)
    scaler_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    incidents = relationship("Incident", back_populates="model_version")
    training_runs = relationship("TrainingRun", back_populates="model_version", cascade="all, delete-orphan")

class TrainingRun(Base):
    __tablename__ = "training_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    model_version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False)
    epoch = Column(Integer, nullable=False)
    train_loss = Column(Float, nullable=True)
    val_loss = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1 = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    confusion_matrix = Column(JSON, default=dict)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    model_version = relationship("ModelVersion", back_populates="training_runs")
