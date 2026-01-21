# app/api/lecturers.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List
from app.core.db import get_session
import app.crud.lecturer as crud_lecturers
from app.schemas.lecturer import LecturerCreate, LecturerPublic

router = APIRouter(
    prefix="/lecturers",
    tags=["Lecturers"]
)

@router.post("", response_model=LecturerPublic)
def create_new_lecturer(
    lecturer: LecturerCreate,
    db: Session = Depends(get_session)
):
    return crud_lecturers.create_lecturer(db, lecturer)

@router.get("", response_model=List[LecturerPublic])
def get_all_lecturers(db: Session = Depends(get_session)):

    return crud_lecturers.get_all_lecturers(db)