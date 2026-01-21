
from sqlmodel import create_engine, Session, SQLModel
from app.core.config import DATABASE_URL
from typing import Generator

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():

    from app.models.profile import Profile, Lecturer
    from app.models.course import Course
    from app.models.schedule import Schedule
    from app.models.enrollment import Enrollment
    from app.models.face_embedding import FaceEmbedding
    from app.models.log import AttendanceLog

    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session