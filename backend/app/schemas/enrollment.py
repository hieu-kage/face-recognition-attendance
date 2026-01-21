from pydantic import BaseModel
from typing import Optional

class EnrollmentSearchFilter(BaseModel):
    course_id: Optional[int] = None
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    page: int = 1
    page_size: int = 20