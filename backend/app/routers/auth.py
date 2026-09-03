from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import User, FarmerProfile
from backend.app.schemas.auth import (
    SendOTPRequest,
    VerifyOTPRequest,
    ResendOTPRequest,
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    OTPResponse
)
from backend.app.schemas.user import UserResponse
from backend.app.services.otp_service import otp_service
from backend.app.auth.security import hash_password, verify_password
from backend.app.auth.jwt import create_access_token
from backend.app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/otp/send", response_model=OTPResponse)
def send_otp(req: SendOTPRequest):
    success, message, dev_otp = otp_service.send_otp(req.phone)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return OTPResponse(success=True, message=message, dev_otp=dev_otp)

@router.post("/otp/resend", response_model=OTPResponse)
def resend_otp(req: ResendOTPRequest):
    success, message, dev_otp = otp_service.send_otp(req.phone)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return OTPResponse(success=True, message=message, dev_otp=dev_otp)

@router.post("/otp/verify", response_model=TokenResponse)
def verify_otp(req: VerifyOTPRequest, db: Session = Depends(get_db)):
    success, message = otp_service.verify_otp(req.phone, req.otp)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    normalized_phone = otp_service.normalize_phone(req.phone)

    # Find or create user
    user = db.query(User).filter(User.phone == normalized_phone).first()
    if not user:
        user = User(
            phone=normalized_phone,
            name=req.name or f"Farmer {normalized_phone[-4:]}",
            is_verified=True,
            preferred_language="en"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create default empty profile
        profile = FarmerProfile(user_id=user.id, primary_crop="Tomato", soil_type="loam")
        db.add(profile)
        db.commit()
        db.refresh(user)
    else:
        if not user.is_verified:
            user.is_verified = True
            db.commit()

    token = create_access_token(data={"sub": str(user.id), "phone": user.phone})
    user_dict = {
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
        "preferred_language": user.preferred_language,
        "location": user.location,
        "is_verified": user.is_verified
    }
    return TokenResponse(access_token=token, token_type="bearer", user=user_dict)

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    normalized_phone = otp_service.normalize_phone(req.phone)

    existing_phone = db.query(User).filter(User.phone == normalized_phone).first()
    if existing_phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already registered")

    if req.email:
        existing_email = db.query(User).filter(User.email == req.email.strip().lower()).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

    user = User(
        phone=normalized_phone,
        name=req.name.strip(),
        email=req.email.strip().lower() if req.email else None,
        password_hash=hash_password(req.password),
        preferred_language=req.preferred_language or "en",
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = FarmerProfile(user_id=user.id, primary_crop="Tomato", soil_type="loam")
    db.add(profile)
    db.commit()

    token = create_access_token(data={"sub": str(user.id), "phone": user.phone})
    user_dict = {
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
        "preferred_language": user.preferred_language,
        "is_verified": user.is_verified
    }
    return TokenResponse(access_token=token, token_type="bearer", user=user_dict)

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    identifier = req.identifier.strip()
    user = None

    if "@" in identifier:
        user = db.query(User).filter(User.email == identifier.lower()).first()
    else:
        norm_phone = otp_service.normalize_phone(identifier)
        user = db.query(User).filter(User.phone == norm_phone).first()

    if not user or not user.password_hash or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid phone/email or password")

    token = create_access_token(data={"sub": str(user.id), "phone": user.phone})
    user_dict = {
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
        "preferred_language": user.preferred_language,
        "location": user.location,
        "is_verified": user.is_verified
    }
    return TokenResponse(access_token=token, token_type="bearer", user=user_dict)

@router.post("/logout")
def logout():
    return {"success": True, "message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
