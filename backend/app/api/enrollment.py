from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    Form, Body
)
from sqlmodel import Session
from typing import Any
from app.schemas.enrollment import EnrollmentSearchFilter
from app.schemas.profile import ProfileCreate
from app.core.db import get_session
import app.crud.enrollment as crud_enrollments

router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)

@router.post(
    "/upload",
    summary="Upload a student list to enroll in a course"
)
async def upload_enrollment_file(
        *,
        db: Session = Depends(get_session),
        course_id: int = Form(..., description="The ID of the course to enroll into"),
        file: UploadFile = File(..., description="Student list file (CSV, Excel, or Image)")
) -> Any:
    try:
        result = await crud_enrollments.enroll_students_from_file(
            db=db,
            course_id=course_id,
            file=file
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/search")
async def search_enrollments(
    *,
    db: Session = Depends(get_session),
    filter_params: EnrollmentSearchFilter = Body(...)
) -> Any:

    result = crud_enrollments.search_enrollments(
        db=db,
        filter=filter_params
    )
    return result
@router.post("/{course_id}/students", summary="Add a student to a course")
async def add_student_to_course(
    *,
    course_id: int,
    student: ProfileCreate,    # name, student_code
    db: Session = Depends(get_session),
):
    try:
        result = crud_enrollments.add_student_to_course(
            db=db,
            course_id=course_id,
            profile_data=student
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error: {str(e)}"
        )