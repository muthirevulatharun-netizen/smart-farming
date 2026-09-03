from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field

class CalendarCreateRequest(BaseModel):
    crop: str = Field(..., description="Target crop e.g. Tomato, Rice, Cotton")
    sowing_date: date = Field(..., description="Sowing or transplanting date (YYYY-MM-DD)")
    location: Optional[str] = None

class CalendarTaskItem(BaseModel):
    id: Optional[int] = None
    crop: str
    stage: str
    task: str
    recommended_date: str
    status: str = "pending"

class CalendarScheduleResponse(BaseModel):
    success: bool = True
    crop: str
    sowing_date: str
    estimated_harvest_date: str
    total_duration_days: int
    tasks: List[CalendarTaskItem]
