from sqlmodel import SQLModel, Field, Relationship, text, Column, DateTime
from typing import Optional
from datetime import datetime


class AttendanceLog(SQLModel, table=True):
    __tablename__ = 'attendance_logs'
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str
    check_in_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text("now()"))
    )
    schedule_id: int = Field(foreign_key="schedules.id")
    profile_id: int = Field(foreign_key="profiles.id")

    schedule: "Schedule" = Relationship(back_populates="attendance_logs")
    profile: "Profile" = Relationship(back_populates="attendance_logs")