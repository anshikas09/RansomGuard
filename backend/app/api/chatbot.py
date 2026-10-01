from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.chatbot import ChatbotConversation
from app.models.incident import Incident
from app.models.endpoint import Endpoint
from app.schemas.chatbot import ChatQueryRequest, ChatQueryResponse
from app.security.rbac import get_current_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=ChatQueryResponse)
async def query_chatbot(
    request: ChatQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q_lower = request.question.lower()
    page = (request.page_context or "dashboard").lower()

    # Contextual data lookup
    active_incidents = db.query(Incident).filter(Incident.status == "new").count()
    online_endpoints = db.query(Endpoint).filter(Endpoint.status == "online").count()

    answer = ""

    if "endpoint" in q_lower or "agent" in q_lower or "connect" in q_lower:
        answer = f"To connect an endpoint: 1. Run `python endpoint_agent/agent.py` on your target VM. 2. The agent registers automatically over HTTPS to localhost:8000/api/v1/endpoints/register. 3. Currently, you have {online_endpoints} active connected endpoint(s)."
    elif "simulation" in q_lower or "lab" in q_lower or "test" in q_lower:
        answer = "The Safe Simulation Lab operates strictly inside `./scratch/ransim_lab/`. It generates synthetic high-entropy file modifications and extension changes (`.docx` -> `.encrypted`) without touching system or personal user files."
    elif "ai" in q_lower or "lstm" in q_lower or "model" in q_lower or "onnx" in q_lower:
        answer = "RansomGuard uses a 2-layer LSTM neural network trained in PyTorch and exported to ONNX format. It evaluates a 10-event rolling window across 8 behavioral features (file size, Shannon entropy, entropy change, mod rate, extension changes, suspicious process, path length, common extension) in under 50ms per sequence."
    elif "incident" in q_lower or "alert" in q_lower or "threat" in q_lower:
        answer = f"RansomGuard automatically generates an Incident when an endpoint's calculated risk score exceeds 80%. Currently there are {active_incidents} active unhandled incident(s) in the system."
    elif "containment" in q_lower or "isolate" in q_lower or "kill" in q_lower:
        answer = "Automated containment triggers when risk score reaches 90.0%+. The agent safely terminates the malicious process matching the lab signature and toggles network isolation status."
    else:
        answer = f"I am RansomGuard Copilot. I am monitoring your SOC workspace (Currently {online_endpoints} endpoints online, {active_incidents} active incidents). Ask me about setting up endpoints, running safe simulations, inspecting AI model pipeline architecture, or incident containment workflows."

    record = ChatbotConversation(
        user_id=current_user.id,
        page_context=page,
        question=request.question,
        answer=answer,
        timestamp=datetime.utcnow()
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ChatQueryResponse(
        id=record.id,
        question=record.question,
        answer=record.answer,
        page_context=record.page_context,
        timestamp=record.timestamp
    )
