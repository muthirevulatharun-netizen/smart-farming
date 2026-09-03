from typing import List
from pydantic import BaseModel

class DiseasePredictionResponse(BaseModel):
    success: bool = True
    crop: str
    disease: str
    confidence: float
    risk_level: str
    symptoms: List[str]
    treatment: List[str]
    prevention: List[str]
    disclaimer: str = "This is an AI-based prediction and should not replace professional agricultural diagnosis."
