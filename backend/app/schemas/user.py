from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class FarmerProfileBase(BaseModel):
    farm_name: Optional[str] = None
    farm_size: Optional[float] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    experience: Optional[int] = None
    primary_crop: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None

class FarmerProfileCreate(FarmerProfileBase):
    pass

class FarmerProfileResponse(FarmerProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    preferred_language: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: str
    preferred_language: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_verified: bool
    profile: Optional[FarmerProfileResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True
