from typing import List, Optional
from pydantic import BaseModel

class WeatherCurrentResponse(BaseModel):
    success: bool = True
    location: str
    temperature: float
    feels_like: Optional[float] = None
    humidity: float
    wind_speed: float
    condition: str
    condition_icon: str
    rain_probability: float
    uv_index: float
    ai_advisory: str

class WeatherForecastDay(BaseModel):
    date: str
    day: str
    temp_max: float
    temp_min: float
    condition: str
    icon: str
    rain_probability: float

class WeatherForecastResponse(BaseModel):
    success: bool = True
    location: str
    current: WeatherCurrentResponse
    forecast: List[WeatherForecastDay]
