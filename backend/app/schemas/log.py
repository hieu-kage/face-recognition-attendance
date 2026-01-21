
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ConfigBase:
    from_attributes = True
class ProfileSimple(BaseModel):
    name: str
    student_id: Optional[str] = None

    class Config(ConfigBase):
        pass


class ScheduleSimple(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    room: Optional[str] = None

    class Config(ConfigBase):
        pass


class CourseBase(BaseModel):
    id: int
    name: str
    course_code: Optional[str] = None

    class Config(ConfigBase):
        pass


# --- Model cho Response (Output) ---

class CourseDetailResponse(CourseBase):
    schedules: List[ScheduleSimple] = []


class AttendanceLogEntry(BaseModel):
    check_in_time: datetime
    status: str
    profile: ProfileSimple

    class Config(ConfigBase):
        pass


# Model quan trọng cho trang Chi tiết Buổi học
class SessionDetailResponse(BaseModel):
    schedule: ScheduleSimple
    attendees: List[AttendanceLogEntry] = []
    absentees: List[ProfileSimple] = []