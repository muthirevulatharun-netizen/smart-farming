from backend.app.routers.auth import router as auth_router
from backend.app.routers.users import router as users_router
from backend.app.routers.crops import router as crops_router
from backend.app.routers.disease import router as disease_router
from backend.app.routers.pest import router as pest_router
from backend.app.routers.chatbot import router as chatbot_router
from backend.app.routers.weather import router as weather_router
from backend.app.routers.fertilizer import router as fertilizer_router
from backend.app.routers.irrigation import router as irrigation_router
from backend.app.routers.calendar import router as calendar_router
from backend.app.routers.dashboard import router as dashboard_router
from backend.app.routers.admin import router as admin_router

__all__ = [
    "auth_router",
    "users_router",
    "crops_router",
    "disease_router",
    "pest_router",
    "chatbot_router",
    "weather_router",
    "fertilizer_router",
    "irrigation_router",
    "calendar_router",
    "dashboard_router",
    "admin_router"
]
