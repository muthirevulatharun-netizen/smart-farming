from typing import Optional, List
from pydantic import BaseModel, Field

class FertilizerRecommendRequest(BaseModel):
    crop: str = Field(..., description="Crop name e.g. Rice, Tomato, Cotton")
    soil_type: Optional[str] = "loam"
    nitrogen: float = Field(..., ge=0, le=300)
    phosphorus: float = Field(..., ge=0, le=300)
    potassium: float = Field(..., ge=0, le=300)
    ph: Optional[float] = Field(6.5, ge=0, le=14)
    growth_stage: Optional[str] = "vegetative"

class NutrientStatus(BaseModel):
    nutrient: str
    current_value: float
    status: str  # "Low", "Optimal", "High"
    target_range: str

class FertilizerRecommendResponse(BaseModel):
    success: bool = True
    crop: str
    nutrient_analysis: List[NutrientStatus]
    general_guidance: str
    organic_recommendations: List[str]
    chemical_recommendations: List[str]
    application_timing: str
    precautions: List[str]
