from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ConfigBase:
    from_attributes = True



class CourseBase(BaseModel):
    id: int
    name: str
    course_code: Optional[str]
    class Config : ConfigBase

class CourseCreateRequest(BaseModel):
    name: str
    course_code: str
    lecturer_id: Optional[int] = None
    template_start_time: datetime
    template_end_time: datetime
    number_of_sessions: int
    template_room: Optional[str] = None


class ScheduleSimple(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    room: Optional[str]
    class Config :ConfigBase

class CourseDetailResponse(CourseBase):
    schedules: List[ScheduleSimple] = []