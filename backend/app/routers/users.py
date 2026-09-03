from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import User, FarmerProfile
from backend.app.schemas.user import FarmerProfileCreate, FarmerProfileResponse, UserUpdate
from backend.app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/profile", tags=["Farmer Profile"])

@router.get("", response_model=FarmerProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    if not profile:
        profile = FarmerProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("", response_model=FarmerProfileResponse)
def update_profile(
    data: FarmerProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    if not profile:
        profile = FarmerProfile(user_id=current_user.id)
        db.add(profile)

    update_data = data.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if val is not None:
            setattr(profile, field, val)

    # Sync primary crop and location back to User model if provided
    if data.district or data.state:
        loc = f"{data.district or ''}, {data.state or ''}".strip(", ")
        current_user.location = loc

    db.commit()
    db.refresh(profile)
    return profile
