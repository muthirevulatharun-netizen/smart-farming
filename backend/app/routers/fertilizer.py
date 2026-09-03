from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import User, Recommendation
from backend.app.schemas.fertilizer import (
    FertilizerRecommendRequest,
    FertilizerRecommendResponse
)
from backend.app.services.fertilizer_service import fertilizer_service
from backend.app.auth.dependencies import get_optional_current_user

router = APIRouter(prefix="/api/fertilizer", tags=["Fertilizer Recommendations"])

@router.post("/recommend", response_model=FertilizerRecommendResponse)
def recommend_fertilizer(
    req: FertilizerRecommendRequest,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    res = fertilizer_service.calculate_recommendations(
        crop=req.crop,
        nitrogen=req.nitrogen,
        phosphorus=req.phosphorus,
        potassium=req.potassium,
        ph=req.ph,
        soil_type=req.soil_type,
        growth_stage=req.growth_stage
    )

    if current_user:
        rec = Recommendation(
            user_id=current_user.id,
            type="fertilizer",
            input_data=req.model_dump(),
            recommendation=res
        )
        db.add(rec)
        db.commit()

    return FertilizerRecommendResponse(**res)
