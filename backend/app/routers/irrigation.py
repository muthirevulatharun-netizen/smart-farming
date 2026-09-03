from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import User, Recommendation
from backend.app.schemas.irrigation import (
    IrrigationRecommendRequest,
    IrrigationRecommendResponse
)
from backend.app.services.irrigation_service import irrigation_service
from backend.app.auth.dependencies import get_optional_current_user

router = APIRouter(prefix="/api/irrigation", tags=["Smart Irrigation"])

@router.post("/recommend", response_model=IrrigationRecommendResponse)
def recommend_irrigation(
    req: IrrigationRecommendRequest,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    res = irrigation_service.calculate_recommendation(
        crop=req.crop,
        soil_type=req.soil_type,
        moisture_level=req.moisture_level,
        temperature=req.temperature,
        humidity=req.humidity,
        recent_rainfall=req.recent_rainfall,
        forecast_rain_prob=req.forecast_rain_prob,
        growth_stage=req.growth_stage
    )

    if current_user:
        rec = Recommendation(
            user_id=current_user.id,
            type="irrigation",
            input_data=req.model_dump(),
            recommendation=res
        )
        db.add(rec)
        db.commit()

    return IrrigationRecommendResponse(**res)
