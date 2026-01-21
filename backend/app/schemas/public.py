from pydantic import BaseModel
from app.schemas.profile import ProfilePublic
class EnrollRequest(BaseModel):
    studentId: str
    name: str
    image_base64: str

class SearchRequest(BaseModel):
    course_id: int
    image_base64: str

class EnrollResponse(BaseModel):
    success: bool = True
    data: ProfilePublic

class SearchResponse(BaseModel):
    success: bool = True
    name: str
    student_id: str