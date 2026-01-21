from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Schedule(SQLModel, table=True):
    __tablename__ = 'schedules'
    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: datetime = Field(index=True)
    end_time: datetime
    room: Optional[str] = None

    course_id: int = Field(foreign_key="courses.id")
    course: "Course" = Relationship(back_populates="schedules")

    # Relationships
    attendance_logs: List["AttendanceLog"] = Relationship(back_populates="schedule")