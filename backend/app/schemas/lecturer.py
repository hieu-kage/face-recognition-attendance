from pydantic import BaseModel

class LecturerCreate(BaseModel):
    name: str
    email: str

class LecturerPublic(BaseModel):
    id: int 
    name: str