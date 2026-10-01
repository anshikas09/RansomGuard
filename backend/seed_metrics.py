import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.model import ModelVersion
from app.api.ml import compute_onnx_metrics

db = SessionLocal()

metrics = compute_onnx_metrics()
print("Computed ONNX Metrics:", json.dumps(metrics, indent=2))

active_model = db.query(ModelVersion).filter(ModelVersion.deployment_status == "active").first()
if not active_model:
    active_model = ModelVersion(
        version="v1.0.0-onnx",
        framework="ONNX",
        input_features=["file_operations", "entropy_delta", "rapid_creates", "directory_traversals", "suspicious_extensions", "is_suspicious_process", "cpu_spikes", "memory_spikes"],
        sequence_length=10,
        training_status="trained",
        last_trained_at=datetime.utcnow(),
        deployment_status="active",
        metrics=metrics,
        onnx_path="../models/ransomware_detector.onnx",
        scaler_path="../models/scaler.pkl"
    )
    db.add(active_model)
else:
    active_model.metrics = metrics
    active_model.last_trained_at = datetime.utcnow()

db.commit()
print("Successfully committed ModelVersion to DB!")
db.close()
