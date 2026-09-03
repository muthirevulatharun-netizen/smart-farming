from typing import Optional
from fastapi import APIRouter, Depends, Query
from backend.app.schemas.weather import WeatherCurrentResponse, WeatherForecastResponse
from backend.app.services.weather_service import weather_service
from backend.app.database.models import User
from backend.app.auth.dependencies import get_optional_current_user

router = APIRouter(prefix="/api/weather", tags=["Weather"])

@router.get("/current", response_model=WeatherCurrentResponse)
def get_current_weather(
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    location: Optional[str] = Query(None, description="Location name"),
    current_user: User = Depends(get_optional_current_user)
):
    latitude = lat or (current_user.latitude if current_user else None)
    longitude = lon or (current_user.longitude if current_user else None)
    loc_name = location or (current_user.location if current_user else None)

    data = weather_service.get_weather(latitude=latitude, longitude=longitude, location_name=loc_name)
    current = data["current"]
    return WeatherCurrentResponse(
        success=True,
        location=data["location"],
        temperature=current["temperature"],
        feels_like=current["feels_like"],
        humidity=current["humidity"],
        wind_speed=current["wind_speed"],
        condition=current["condition"],
        condition_icon=current["condition_icon"],
        rain_probability=current["rain_probability"],
        uv_index=current["uv_index"],
        ai_advisory=current["ai_advisory"]
    )

@router.get("/forecast", response_model=WeatherForecastResponse)
def get_weather_forecast(
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    location: Optional[str] = Query(None),
    current_user: User = Depends(get_optional_current_user)
):
    latitude = lat or (current_user.latitude if current_user else None)
    longitude = lon or (current_user.longitude if current_user else None)
    loc_name = location or (current_user.location if current_user else None)

    data = weather_service.get_weather(latitude=latitude, longitude=longitude, location_name=loc_name)
    return WeatherForecastResponse(**data)
