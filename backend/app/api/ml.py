from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import numpy as np
import logging

from app.core.database import get_db
from app.models.model import ModelVersion, TrainingRun
from app.schemas.ml import ModelVersionResponse, TrainModelRequest
from app.security.rbac import get_current_user, require_role
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

def compute_onnx_metrics() -> Optional[Dict[str, Any]]:
    """
    Dynamically evaluates the active ONNX model against test artifacts (X_test.npy, y_test.npy).
    Returns real computed metrics or None if artifacts are missing.
    """
    model_candidates = [
        os.getenv("MODEL_PATH", "./models/ransomware_detector.onnx"),
        "./models/ransomware_detector.onnx",
        "../models/ransomware_detector.onnx"
    ]
    X_candidates = ["./models/X_test.npy", "../models/X_test.npy"]
    y_candidates = ["./models/y_test.npy", "../models/y_test.npy"]

    model_path = next((p for p in model_candidates if os.path.exists(p)), None)
    X_test_path = next((p for p in X_candidates if os.path.exists(p)), None)
    y_test_path = next((p for p in y_candidates if os.path.exists(p)), None)

    if not (model_path and X_test_path and y_test_path):
        return None

    try:
        import onnxruntime as ort
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

        X_test = np.load(X_test_path)
        y_test = np.load(y_test_path)
        session = ort.InferenceSession(model_path)
        input_name = session.get_inputs()[0].name

        y_probs = []
        for i in range(len(X_test)):
            sample = np.expand_dims(X_test[i], axis=0).astype(np.float32)
            out = session.run(None, {input_name: sample})
            y_probs.append(float(out[0][0][0]))

        y_probs = np.array(y_probs)
        y_preds = (y_probs >= 0.5).astype(int)

        acc = float(accuracy_score(y_test, y_preds))
        prec = float(precision_score(y_test, y_preds, zero_division=0))
        rec = float(recall_score(y_test, y_preds, zero_division=0))
        f1 = float(f1_score(y_test, y_preds, zero_division=0))
        auc = float(roc_auc_score(y_test, y_probs)) if len(np.unique(y_test)) > 1 else 1.0
        cm = confusion_matrix(y_test, y_preds)

        return {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "roc_auc": round(auc, 4),
            "confusion_matrix": {
                "tn": int(cm[0][0]),
                "fp": int(cm[0][1]),
                "fn": int(cm[1][0]),
                "tp": int(cm[1][1])
            },
            "test_samples": len(X_test),
            "evaluation_status": "evaluated"
        }
    except Exception as e:
        logger.warning(f"Failed to dynamically evaluate ONNX model: {e}")
        return None

@router.get("/versions", response_model=List[ModelVersionResponse])
async def list_model_versions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    versions = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).all()
    metrics = compute_onnx_metrics() or {
        "accuracy": 0.0,
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
        "roc_auc": 0.0,
        "evaluation_status": "Not evaluated"
    }

    if not versions:
        default_ver = ModelVersion(
            version="v1.0-lstm-onnx",
            framework="PyTorch 2.0 / ONNX 1.14",
            input_features=[
                "file_size", "entropy", "entropy_change", "mod_rate",
                "ext_changed", "is_suspicious_process", "file_path_length", "is_common_extension"
            ],
            sequence_length=10,
            training_status="completed",
            last_trained_at=datetime.utcnow(),
            deployment_status="active",
            metrics=metrics,
            onnx_path="./models/ransomware_detector.onnx"
        )
        db.add(default_ver)
        db.commit()
        db.refresh(default_ver)
        return [default_ver]

    # Update active model metrics dynamically from real evaluation results
    for v in versions:
        if v.deployment_status == "active" and metrics:
            v.metrics = metrics
            db.add(v)
    db.commit()
    return versions

@router.get("/active", response_model=ModelVersionResponse)
async def get_active_model(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    model = db.query(ModelVersion).filter(ModelVersion.deployment_status == "active").first()
    metrics = compute_onnx_metrics()
    if not model:
        versions = await list_model_versions(db, current_user)
        return versions[0]
    if metrics:
        model.metrics = metrics
    return model

@router.get("/pipeline-info")
async def get_pipeline_info(current_user: User = Depends(get_current_user)):
    metrics = compute_onnx_metrics()
    return {
        "pipeline_name": "RansomGuard LSTM Behavioral Engine",
        "input_shape": [1, 10, 8],
        "feature_names": [
            "file_size (bytes)",
            "entropy (Shannon 0-8)",
            "entropy_change",
            "mod_rate (sec between ops)",
            "ext_changed (0/1)",
            "is_suspicious_process (0/1)",
            "file_path_length",
            "is_common_extension (0/1)"
        ],
        "sequence_window": 10,
        "inference_engine": "ONNX Runtime v1.14+",
        "active_metrics": metrics or "Not evaluated"
    }
