
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.db import get_session
import app.crud.schedule as crud_schedules
from app.schemas.log import SessionDetailResponse

router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"]
)

@router.get("/{schedule_id}")
def get_schedule_detail(
    schedule_id: int,
    db: Session = Depends(get_session)
):
    return crud_schedules.get_session_data(db, schedule_id)