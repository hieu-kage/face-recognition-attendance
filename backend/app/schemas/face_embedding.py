from pydantic import BaseModel
from typing import List



class EnrollRequest(BaseModel):
    studentId: str
    name: str
    image_base64: str


class SearchRequest(BaseModel):
    schedule_id: int
    image_base64: str