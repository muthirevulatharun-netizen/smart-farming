import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import FarmingCalendar, User, FarmerProfile
from backend.app.schemas.calendar import (
    CalendarCreateRequest,
    CalendarScheduleResponse
)
from backend.app.services.calendar_service import calendar_service
from backend.app.auth.dependencies import get_current_user, get_optional_current_user

router = APIRouter(prefix="/api/calendar", tags=["Farming Calendar"])

@router.post("/create", response_model=CalendarScheduleResponse)
def create_calendar(
    req: CalendarCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schedule = calendar_service.generate_schedule(
        crop=req.crop,
        sowing_date=req.sowing_date,
        location=req.location
    )

    # Delete existing calendar tasks for this crop and insert new
    db.query(FarmingCalendar).filter(
        FarmingCalendar.user_id == current_user.id,
        FarmingCalendar.crop == req.crop.capitalize()
    ).delete()

    sowing_dt = datetime.datetime.combine(req.sowing_date, datetime.time.min)
    for task_item in schedule["tasks"]:
        rec_dt = datetime.datetime.strptime(task_item["recommended_date"], "%Y-%m-%d")
        cal_record = FarmingCalendar(
            user_id=current_user.id,
            crop=req.crop.capitalize(),
            sowing_date=sowing_dt,
            stage=task_item["stage"],
            task=task_item["task"],
            recommended_date=rec_dt,
            status=task_item["status"]
        )
        db.add(cal_record)

    db.commit()
    return CalendarScheduleResponse(**schedule)

@router.get("", response_model=CalendarScheduleResponse)
def get_calendar(
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    crop_name = "Tomato"
    if current_user and current_user.profile and current_user.profile.primary_crop:
        crop_name = current_user.profile.primary_crop

    today = datetime.date.today()
    default_sowing = today - datetime.timedelta(days=30)
    schedule = calendar_service.generate_schedule(crop=crop_name, sowing_date=default_sowing)
    return CalendarScheduleResponse(**schedule)
