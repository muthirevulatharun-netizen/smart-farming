from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import Crop, Recommendation, User
from backend.app.schemas.crop import (
    CropRecommendationRequest,
    CropRecommendationResponse,
    CropDetailResponse
)
from backend.app.ml.crop_model import crop_engine
from backend.app.auth.dependencies import get_optional_current_user

router = APIRouter(prefix="/api/crop", tags=["Crops & ML Recommendation"])

@router.post("/recommend", response_model=CropRecommendationResponse)
def recommend_crop(
    req: CropRecommendationRequest,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Predict top recommended crop using Scikit-Learn Random Forest model."""
    result = crop_engine.predict(
        nitrogen=req.nitrogen,
        phosphorus=req.phosphorus,
        potassium=req.potassium,
        temperature=req.temperature,
        humidity=req.humidity,
        ph=req.ph,
        rainfall=req.rainfall
    )

    # Save to recommendations table if authenticated
    if current_user:
        rec = Recommendation(
            user_id=current_user.id,
            type="crop",
            input_data=req.model_dump(),
            recommendation=result
        )
        db.add(rec)
        db.commit()

    return CropRecommendationResponse(
        success=True,
        recommended_crop=result["recommended_crop"],
        confidence=result["confidence"],
        suitable_season=result["suitable_season"],
        guidance=result["guidance"],
        alternatives=result["alternatives"]
    )

@router.get("/all", response_model=List[CropDetailResponse])
def get_all_crops(db: Session = Depends(get_db)):
    crops = db.query(Crop).all()
    if not crops:
        # Seed standard Indian crops if empty
        seed_crops = [
            Crop(name="Tomato", scientific_name="Solanum lycopersicum", season="Kharif/Rabi", soil_type="Loam", min_temperature=18, max_temperature=32, rainfall=600, humidity=65, description="High-value horticultural crop."),
            Crop(name="Rice", scientific_name="Oryza sativa", season="Kharif", soil_type="Clay loam", min_temperature=20, max_temperature=35, rainfall=1200, humidity=80, description="Staple cereal of India."),
            Crop(name="Cotton", scientific_name="Gossypium", season="Kharif", soil_type="Black soil", min_temperature=21, max_temperature=32, rainfall=750, humidity=60, description="White gold cash crop of Deccan plateau."),
            Crop(name="Chilli", scientific_name="Capsicum annuum", season="Kharif/Rabi", soil_type="Sandy loam", min_temperature=20, max_temperature=30, rainfall=650, humidity=60, description="Major spice and cash crop.")
        ]
        db.add_all(seed_crops)
        db.commit()
        crops = db.query(Crop).all()
    return crops

@router.get("/{crop_id}", response_model=CropDetailResponse)
def get_crop_by_id(crop_id: int, db: Session = Depends(get_db)):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop
