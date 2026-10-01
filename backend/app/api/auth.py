from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.session import Session as UserSession
from app.models.audit_log import AuditLog
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.security.auth import create_access_token
from app.security.rbac import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered."
        )

    # First registered user can default to admin role for convenience
    user_count = db.query(User).count()
    assigned_role = request.role or ("admin" if user_count == 0 else "viewer")

    user = User(
        email=request.email,
        full_name=request.full_name,
        organization=request.organization or "Security Lab",
        role=assigned_role
    )
    user.set_password(request.password)

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    session_record = UserSession(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=1440)
    )
    db.add(session_record)

    audit = AuditLog(
        user_id=user.id,
        action="USER_SIGNUP",
        result="success",
        details={"email": user.email, "role": user.role}
    )
    db.add(audit)
    db.commit()

    logger.info(f"User registered: {user.email} with role {user.role}")

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            organization=user.organization,
            role=user.role,
            is_active=user.is_active
        )
    )

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email credentials or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )

    token = create_access_token({"sub": str(user.id)})
    session_record = UserSession(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=1440)
    )
    db.add(session_record)

    audit = AuditLog(
        user_id=user.id,
        action="USER_LOGIN",
        result="success",
        details={"email": user.email}
    )
    db.add(audit)
    db.commit()

    logger.info(f"User logged in: {user.email}")

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            organization=user.organization,
            role=user.role,
            is_active=user.is_active
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        organization=current_user.organization,
        role=current_user.role,
        is_active=current_user.is_active
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(UserSession).filter(UserSession.user_id == current_user.id).delete()
    audit = AuditLog(
        user_id=current_user.id,
        action="USER_LOGOUT",
        result="success"
    )
    db.add(audit)
    db.commit()
    return {"message": "Successfully logged out"}
