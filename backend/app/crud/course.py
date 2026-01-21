
from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from datetime import timedelta
from fastapi.encoders import jsonable_encoder
from app.models.course import Course
from app.models.schedule import Schedule
from app.models.profile import Profile, Lecturer
from app.schemas.course import CourseCreateRequest

def create_course(db: Session, course: CourseCreateRequest):
    try:
        new_course = Course.from_orm(course)
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
        schedules_to_add = []
        if new_course.number_of_sessions and new_course.template_start_time:
            for i in range(new_course.number_of_sessions):
                start_time = new_course.template_start_time + timedelta(weeks=i)
                end_time = new_course.template_end_time + timedelta(weeks=i)

                schedule = Schedule(
                    course_id=new_course.id,
                    start_time=start_time,
                    end_time=end_time,
                    room=new_course.template_room
                )
                schedules_to_add.append(schedule)

            db.add_all(schedules_to_add)
            db.commit()

        return new_course
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo khóa học: {str(e)}")

def get_all_courses(db: Session):
    courses = db.exec(
        select(Course)
        .options(
            selectinload(Course.lecturer).selectinload(Lecturer.profile),
            selectinload(Course.schedules)
        )
    ).all()

    result = []
    for c in courses:
        course_dict = {
            "id": c.id,
            "name": c.name,
            "course_code": c.course_code,
            "lecturer": {
                "id": c.lecturer.id,
                "profile": {
                    "id": c.lecturer.profile.id,
                    "full_name": c.lecturer.profile.name,
                    "role": c.lecturer.profile.role
                }
            } if c.lecturer else None,
            "schedules": [
                {
                    "id": s.id,
                    "start_time": s.start_time.isoformat(),
                    "end_time": s.end_time.isoformat(),
                    "room": s.room
                } for s in c.schedules
            ]
        }
        result.append(course_dict)

    return result

def get_course_details(db: Session, course_id: int):

    statement = select(Course).where(Course.id == course_id).options(
        selectinload(Course.schedules)
    )
    course = db.exec(statement).first()
    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy khóa học")
    return course