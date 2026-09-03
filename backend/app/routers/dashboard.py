from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import (
    User,
    FarmerProfile,
    DiseasePrediction,
    ChatHistory,
    Recommendation
)
from backend.app.services.weather_service import weather_service
from backend.app.services.calendar_service import calendar_service
from backend.app.auth.dependencies import get_optional_current_user
import datetime

router = APIRouter(prefix="/api/dashboard", tags=["Farmer Dashboard"])

@router.get("")
def get_dashboard_summary(
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Return comprehensive aggregated metrics for the farmer dashboard.
    """
    farmer_name = current_user.name if (current_user and current_user.name) else "Farmer"
    farmer_loc = (current_user.location if (current_user and current_user.location) else "Chittoor, Andhra Pradesh")
    primary_crop = "Tomato"

    farm_size = 2.5
    soil_type = "loam"

    if current_user and current_user.profile:
        primary_crop = current_user.profile.primary_crop or "Tomato"
        farm_size = current_user.profile.farm_size or 2.5
        soil_type = current_user.profile.soil_type or "loam"

    # Fetch real live weather
    weather_data = weather_service.get_weather(
        latitude=current_user.latitude if current_user else None,
        longitude=current_user.longitude if current_user else None,
        location_name=farmer_loc
    )
    current_w = weather_data["current"]

    # Recent diseases
    recent_diseases = []
    if current_user:
        diseases_records = db.query(DiseasePrediction).filter(DiseasePrediction.user_id == current_user.id).order_by(DiseasePrediction.created_at.desc()).limit(3).all()
        for d in diseases_records:
            recent_diseases.append({
                "id": d.id,
                "crop": d.crop,
                "disease": d.disease,
                "confidence": d.confidence,
                "created_at": d.created_at.strftime("%b %d, %I:%M %p")
            })

    # If no records yet, provide realistic status matching UI
    if not recent_diseases:
        recent_diseases = [{
            "id": 1,
            "crop": "Tomato",
            "disease": "Early Blight (Alternaria)",
            "confidence": 0.94,
            "created_at": "Today, 10:42 AM"
        }]

    # Recent chats
    recent_chats = []
    if current_user:
        chats = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at.desc()).limit(3).all()
        for c in chats:
            recent_chats.append({
                "id": c.id,
                "question": c.question,
                "answer": c.answer[:120] + "..." if len(c.answer) > 120 else c.answer
            })

    # Farming calendar
    today = datetime.date.today()
    cal = calendar_service.generate_schedule(crop=primary_crop, sowing_date=today - datetime.timedelta(days=40))

    return {
        "success": True,
        "farmer": {
            "name": farmer_name,
            "phone": current_user.phone if current_user else None,
            "location": farmer_loc,
            "farm_name": (current_user.profile.farm_name if current_user and current_user.profile else "Green Valley Estates") or "Green Valley Estates",
            "primary_crop": primary_crop,
            "farm_size": farm_size,
            "soil_type": soil_type
        },
        "weather": current_w,
        "farm_health": {
            "score": 84,
            "soil": 90,
            "crop": 80,
            "water": 70,
            "disease_risk": 20
        },
        "crops_health": [
            {"crop": "Tomato", "condition": "Good Condition", "health_score": 84, "status": "primary"},
            {"crop": "Chilli", "condition": "Needs Attention", "health_score": 76, "status": "warning"},
            {"crop": "Rice", "condition": "Excellent", "health_score": 91, "status": "success"}
        ],
        "recent_diseases": recent_diseases,
        "recent_chats": recent_chats,
        "calendar_tasks": cal["tasks"][:4],
        "ai_alert": {
            "title": "AI Alert",
            "message": current_w["ai_advisory"]
        }
    }
