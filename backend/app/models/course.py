from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Course(SQLModel, table=True):
    __tablename__ = 'courses'
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    course_code: Optional[str] = Field(default=None, unique=True)

    lecturer_id: Optional[int] = Field(default=None, foreign_key="lecturers.id")
    lecturer: Optional["Lecturer"] = Relationship(back_populates="courses")

    template_start_time: Optional[datetime] = None
    template_end_time: Optional[datetime] = None
    number_of_sessions: Optional[int] = None
    template_room: Optional[str] = None

    schedules: List["Schedule"] = Relationship(back_populates="course")
    enrollments: List["Enrollment"] = Relationship(back_populates="course")