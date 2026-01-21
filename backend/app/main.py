from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import face_embedding, log,course,lecturer,enrollment,schedule

from app.core.db import create_db_and_tables
app = FastAPI(title="FaceID Attendance API")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://face-recognize-two.vercel.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
app.include_router(log.router)
app.include_router(face_embedding.router)
app.include_router(course.router)
app.include_router(lecturer.router)
app.include_router(enrollment.router)
app.include_router(schedule.router)
@app.get("/")
def read_root():
    return {"message": "Face ID Backend Service"}