from typing import Optional
from pydantic import BaseModel, Field

class IrrigationRecommendRequest(BaseModel):
    crop: Optional[str] = "Tomato"
    soil_type: Optional[str] = "loam"
    moisture_level: Optional[float] = Field(None, ge=0, le=100, description="Measured soil moisture percentage")
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    recent_rainfall: Optional[float] = Field(0.0, description="Rainfall in last 24 hours in mm")
    forecast_rain_prob: Optional[float] = Field(None, description="Forecasted chance of rain %")
    growth_stage: Optional[str] = "vegetative"

class IrrigationRecommendResponse(BaseModel):
    success: bool = True
    irrigation_required: bool
    recommended_time: str
    estimated_water_liters_per_acre: float
    moisture_percentage: float
    reason: str
    is_estimate: bool = True
