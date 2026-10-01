from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import json

from app.core.database import Base, engine
from app.api import auth, endpoints, telemetry, incidents, ml, simulation, chatbot, health, demo
from app.core.websocket_manager import ws_manager

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RansomGuard Backend Service...")
    # Auto-create database tables on startup (PostgreSQL or SQLite)
    Base.metadata.create_all(bind=engine)
    logger.info("Database schemas initialized.")

    sim_dir = os.getenv("SIMULATION_DIRECTORY", "./scratch/ransim_lab")
    os.makedirs(sim_dir, exist_ok=True)
    os.makedirs("./models", exist_ok=True)
    yield
    logger.info("RansomGuard Backend Service shutting down...")

app = FastAPI(
    title="RansomGuard API",
    description="AI-Powered Cloud-Native Ransomware Detection & Auto-Containment System",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production config can restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API V1 routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(endpoints.router, prefix="/api/v1/endpoints", tags=["Endpoints"])
app.include_router(telemetry.router, prefix="/api/v1/telemetry", tags=["Telemetry"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
app.include_router(ml.router, prefix="/api/v1/ml", tags=["Machine Learning"])
app.include_router(simulation.router, prefix="/api/v1/simulation", tags=["Simulation"])
app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["Chatbot"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health Check"])
app.include_router(demo.router, prefix="/api/v1/demo", tags=["Demo Management"])

@app.get("/")
async def root():
    return {
        "title": "RansomGuard Defense System API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming client ping/messages
            await websocket.send_text(json.dumps({"type": "PONG", "message": "Heartbeat acknowledged"}))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
