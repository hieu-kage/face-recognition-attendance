from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID
class Profile(SQLModel, table=True):
    __tablename__ = 'profiles'
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[UUID] = Field(default=None, unique=True)
    student_id: Optional[str] = Field(default=None, unique=True)
    name: str = Field(index=True)
    role: str = Field(default='student')

    # Relationships
    lecturer: Optional["Lecturer"] = Relationship(back_populates="profile")
    face_embedding: Optional["FaceEmbedding"] = Relationship(back_populates="profile")
    enrollments: List["Enrollment"] = Relationship(back_populates="profile")
    attendance_logs: List["AttendanceLog"] = Relationship(back_populates="profile")


class Lecturer(SQLModel, table=True):
    __tablename__ = 'lecturers'
    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(foreign_key="profiles.id", unique=True)

    profile: "Profile" = Relationship(back_populates="lecturer")
    courses: List["Course"] = Relationship(back_populates="lecturer")