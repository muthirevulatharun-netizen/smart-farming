from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import ChatHistory, User, FarmerProfile
from backend.app.schemas.chatbot import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse
)
from backend.app.services.ai_service import ai_service
from backend.app.services.weather_service import weather_service
from backend.app.auth.dependencies import get_optional_current_user

router = APIRouter(prefix="/api/chat", tags=["AI Chatbot"])

@router.post("", response_model=ChatMessageResponse)
def chat(
    req: ChatMessageRequest,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    # Assemble rich farming context
    context = req.context or {}
    if current_user:
        context["farmer_name"] = current_user.name
        context["preferred_language"] = current_user.preferred_language
        context["location"] = current_user.location or "Chittoor, Andhra Pradesh"
        profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
        if profile:
            context["primary_crop"] = profile.primary_crop
            context["soil_type"] = profile.soil_type
            context["farm_size"] = profile.farm_size

    # Fetch live weather snapshot for context
    weather_data = weather_service.get_weather()
    current_w = weather_data.get("current", {})
    context["temperature"] = current_w.get("temperature", 32)
    context["humidity"] = current_w.get("humidity", 60)
    context["rain_probability"] = current_w.get("rain_probability", 15)

    res = ai_service.generate_chat_response(
        message=req.message,
        crop=req.crop or context.get("primary_crop"),
        language=req.language or "en",
        context=context
    )

    # Save conversation to database if user is logged in
    if current_user:
        history_entry = ChatHistory(
            user_id=current_user.id,
            question=req.message,
            answer=res["answer"],
            language=res["language"],
            context_used=context
        )
        db.add(history_entry)
        db.commit()

    return ChatMessageResponse(
        success=True,
        answer=res["answer"],
        language=res["language"],
        context_used=context
    )

@router.get("/history", response_model=ChatHistoryResponse)
def get_chat_history(
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return ChatHistoryResponse(success=True, history=[])

    items = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at.desc()).limit(30).all()
    # Reverse to return in chronological order
    items_reversed = list(reversed(items))
    return ChatHistoryResponse(success=True, history=items_reversed)
