
from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List

from app.core.db import get_session
import app.crud.course as crud_courses
from app.schemas.course import CourseCreateRequest, CourseDetailResponse
from app.models.course import Course

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)

@router.post("", response_model=Course)
def create_new_course(
    course: CourseCreateRequest,
    db: Session = Depends(get_session)
):
    return crud_courses.create_course(db, course)

@router.get("")
def get_all_courses(db: Session = Depends(get_session)):

    return crud_courses.get_all_courses(db)

@router.get("/{course_id}", response_model=CourseDetailResponse)
def get_course_details(course_id: int, db: Session = Depends(get_session)):

    course = crud_courses.get_course_details(db, course_id)
    return course