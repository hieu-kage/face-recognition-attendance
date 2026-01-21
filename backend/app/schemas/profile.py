from typing import List, Optional
from pydantic import BaseModel


class ProfilePublic(BaseModel):
    id: int
    student_id: str | None
    name: str
    role: str

    class Config:
        from_attributes = True

class ProfileCreate(BaseModel):
    name: str
    student_id: str