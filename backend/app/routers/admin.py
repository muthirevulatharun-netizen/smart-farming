from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import User, Crop, DiseasePrediction, ChatHistory, Recommendation

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/metrics")
def get_admin_metrics(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_crops = db.query(Crop).count()
    total_diseases = db.query(DiseasePrediction).count()
    total_chats = db.query(ChatHistory).count()
    total_recs = db.query(Recommendation).count()

    return {
        "success": True,
        "metrics": {
            "total_registered_farmers": total_users,
            "total_crop_records": total_crops,
            "total_disease_predictions": total_diseases,
            "total_chatbot_queries": total_chats,
            "total_recommendations": total_recs,
            "system_status": "All AI/ML Services Operational"
        }
    }
