from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Enrollment(SQLModel, table=True):
    __tablename__ = 'enrollments'
    id: Optional[int] = Field(default=None, primary_key=True)

    profile_id: int = Field(foreign_key="profiles.id")
    course_id: int = Field(foreign_key="courses.id")

    profile: "Profile" = Relationship(back_populates="enrollments")
    course: "Course" = Relationship(back_populates="enrollments")