from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form
from backend.app.ml.pest_model import pest_engine

router = APIRouter(prefix="/api/pest", tags=["Pest Identification"])

@router.post("/predict")
async def predict_pest(
    pest_hint: Optional[str] = Form(None),
    crop_hint: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Identify crop pest with symptoms, IPM control guidelines, and prevention.
    """
    res = pest_engine.predict(pest_type=pest_hint, crop=crop_hint)
    return res
