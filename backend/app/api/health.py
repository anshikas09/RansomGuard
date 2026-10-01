from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import os
import time

from app.core.database import get_db
from app.models.model import ModelVersion
from app.models.endpoint import Endpoint
from app.api.ml import compute_onnx_metrics

router = APIRouter()

@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    from app.ml.onnx_runner import inference_engine
    model_exists = inference_engine.session is not None or os.path.exists(inference_engine.model_path)
    model_status = "loaded" if model_exists else "rule_engine_fallback"

    sim_dir = os.getenv("SIMULATION_DIRECTORY", "./scratch/ransim_lab")
    sim_status = "configured"
    if not os.path.exists(sim_dir):
        try:
            os.makedirs(sim_dir, exist_ok=True)
        except Exception:
            sim_status = "error"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "backend": "online",
            "database": db_status,
            "ml_model": model_status,
            "simulation_directory": sim_status
        }
    }

@router.get("/components")
async def component_health(db: Session = Depends(get_db)):
    db_latency_ms = 0.0
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        db_latency_ms = round((time.time() - start) * 1000, 2)
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    from app.ml.onnx_runner import inference_engine
    model_exists = inference_engine.session is not None or os.path.exists(inference_engine.model_path)
    active_model = db.query(ModelVersion).filter(ModelVersion.deployment_status == "active").first()
    endpoint_count = db.query(Endpoint).count()

    onnx_metrics = compute_onnx_metrics()

    return {
        "database": {
            "status": db_status,
            "latency_ms": db_latency_ms
        },
        "ml_model": {
            "status": "loaded" if model_exists else "ready_to_train",
            "active_version": active_model.version if active_model else "v1.0-lstm-onnx",
            "metrics": onnx_metrics or "Not evaluated"
        },
        "websocket": {
            "status": "active"
        },
        "endpoints": {
            "registered_count": endpoint_count
        },
        "alerting": {
            "status": "configured" if os.getenv("SLACK_WEBHOOK_URL") else "in_app_only"
        }
    }
