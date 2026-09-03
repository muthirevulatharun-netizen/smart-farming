from typing import List, Optional
from pydantic import BaseModel, Field

class CropRecommendationRequest(BaseModel):
    nitrogen: float = Field(..., ge=0, le=300, description="Nitrogen content in soil (mg/kg)")
    phosphorus: float = Field(..., ge=0, le=300, description="Phosphorus content in soil (mg/kg)")
    potassium: float = Field(..., ge=0, le=300, description="Potassium content in soil (mg/kg)")
    temperature: float = Field(..., ge=-10, le=60, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity in percentage")
    ph: float = Field(..., ge=0, le=14, description="pH value of soil")
    rainfall: float = Field(..., ge=0, le=3000, description="Rainfall in mm")

class AlternativeCrop(BaseModel):
    crop: str
    confidence: float

class CropRecommendationResponse(BaseModel):
    success: bool = True
    recommended_crop: str
    confidence: float
    suitable_season: str
    guidance: str
    alternatives: List[AlternativeCrop] = []

class CropDetailResponse(BaseModel):
    id: int
    name: str
    scientific_name: Optional[str]
    season: Optional[str]
    soil_type: Optional[str]
    min_temperature: Optional[float]
    max_temperature: Optional[float]
    rainfall: Optional[float]
    humidity: Optional[float]
    description: Optional[str]

    class Config:
        from_attributes = True
