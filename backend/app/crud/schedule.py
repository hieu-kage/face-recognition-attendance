
from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.models.schedule import Schedule
from app.models.log import AttendanceLog
from app.models.course import Course
from app.models.enrollment import Enrollment

def get_session_data(db: Session, schedule_id: int):

    statement = select(Schedule).where(Schedule.id == schedule_id).options(
        selectinload(Schedule.attendance_logs).selectinload(AttendanceLog.profile),
        selectinload(Schedule.course).selectinload(Course.enrollments).selectinload(Enrollment.profile)
    )

    schedule = db.exec(statement).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Không tìm thấy buổi học")

    attendees_logs = schedule.attendance_logs
    attended_ids = {log.profile_id for log in attendees_logs}

    attendees = []
    for log in attendees_logs:
        attendees.append({
            "id": log.id,
            "schedule_id": log.schedule_id,
            "profile_id": log.profile_id,
            "status": log.status,
            "check_in_time": log.check_in_time,
            "profile": {
                "id": log.profile.id,
                "name": log.profile.name,
                "student_id": log.profile.student_id,
                "role": log.profile.role,
            } if log.profile else None
        })

    absentees = []
    if schedule.course and schedule.course.enrollments:
        for enrollment in schedule.course.enrollments:
            if enrollment.profile_id not in attended_ids and enrollment.profile:
                absentees.append({
                    "id": enrollment.profile.id,
                    "name": enrollment.profile.name,
                    "student_id": enrollment.profile.student_id,
                    "role": enrollment.profile.role
                })

    return {
        "schedule": schedule,
        "attendees": attendees,
        "absentees": absentees
    }
