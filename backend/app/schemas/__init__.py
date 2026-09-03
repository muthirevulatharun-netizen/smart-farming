from backend.app.schemas.auth import (
    SendOTPRequest,
    VerifyOTPRequest,
    ResendOTPRequest,
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    OTPResponse
)
from backend.app.schemas.user import (
    UserResponse,
    UserUpdate,
    FarmerProfileCreate,
    FarmerProfileResponse
)
from backend.app.schemas.crop import (
    CropRecommendationRequest,
    CropRecommendationResponse,
    CropDetailResponse
)
from backend.app.schemas.disease import DiseasePredictionResponse
from backend.app.schemas.chatbot import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse
)
from backend.app.schemas.weather import (
    WeatherCurrentResponse,
    WeatherForecastResponse
)
from backend.app.schemas.irrigation import (
    IrrigationRecommendRequest,
    IrrigationRecommendResponse
)
from backend.app.schemas.fertilizer import (
    FertilizerRecommendRequest,
    FertilizerRecommendResponse
)
from backend.app.schemas.calendar import (
    CalendarCreateRequest,
    CalendarScheduleResponse
)

__all__ = [
    "SendOTPRequest",
    "VerifyOTPRequest",
    "ResendOTPRequest",
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "OTPResponse",
    "UserResponse",
    "UserUpdate",
    "FarmerProfileCreate",
    "FarmerProfileResponse",
    "CropRecommendationRequest",
    "CropRecommendationResponse",
    "CropDetailResponse",
    "DiseasePredictionResponse",
    "ChatMessageRequest",
    "ChatMessageResponse",
    "ChatHistoryResponse",
    "WeatherCurrentResponse",
    "WeatherForecastResponse",
    "IrrigationRecommendRequest",
    "IrrigationRecommendResponse",
    "FertilizerRecommendRequest",
    "FertilizerRecommendResponse",
    "CalendarCreateRequest",
    "CalendarScheduleResponse"
]
