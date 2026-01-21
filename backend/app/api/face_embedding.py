from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, text
import httpx
from app.core.db import get_session
from app.models.profile import Profile
from app.schemas.profile import ProfilePublic
from app.schemas.public import (
    EnrollRequest,
    SearchRequest,
    EnrollResponse,
    SearchResponse,
)

import os

AI_SERVICE_BASE_URL = os.getenv("AI_SERVICE_BASE_URL", "http://localhost:8080")
AI_EMBEDDING_ENDPOINT = f"{AI_SERVICE_BASE_URL}/api/embedding"
AI_EMBEDDING_ENDPOINT = f"{AI_SERVICE_BASE_URL}/api/embedding"
AI_HEALTH_ENDPOINT = f"{AI_SERVICE_BASE_URL}/health"

router = APIRouter(
    prefix="/face_embedding",
    tags=["Face_Embedding"]
)


async def get_embedding_from_api(image_base64: str) -> list:

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                AI_EMBEDDING_ENDPOINT,
                json={"image_base64": image_base64}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Embedding API error: {response.text}"
                )

            result = response.json()
            embedding = result.get("embedding")

            if not embedding:
                raise HTTPException(
                    status_code=500,
                    detail="Dont detect face in the image or embedding missing in response"
                )

            return embedding

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Embedding API timeout (AI Service quá tải hoặc phản hồi chậm)"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to embedding API at {AI_SERVICE_BASE_URL}. Is it running? Error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error calling embedding API: {str(e)}"
        )


@router.post("/enroll", response_model=EnrollResponse)
async def enroll_face(
        request: EnrollRequest,
        session: Session = Depends(get_session)
):
    vector = await get_embedding_from_api(request.image_base64)
    vector_str = str(list(vector))

    try:

        profile = session.query(Profile).filter(Profile.student_id == request.studentId).first()

        if not profile:
            profile = Profile(
                student_id=request.studentId,
                name=request.name,
                role='student'
            )
            session.add(profile)
            session.flush()

        check_exist = session.execute(
            text("SELECT id FROM face_embeddings WHERE profile_id = :pid"),
            {"pid": profile.id}
        ).fetchone()

        if check_exist:
            update_sql = text("""
                              UPDATE face_embeddings
                              SET embedding = :vec
                              WHERE profile_id = :pid
                              """)
            session.execute(update_sql, {"pid": profile.id, "vec": vector_str})
        else:
            insert_sql = text("""
                              INSERT INTO face_embeddings (profile_id, embedding)
                              VALUES (:pid, :vec)
                              """)
            session.execute(insert_sql, {"pid": profile.id, "vec": vector_str})


        session.commit()
        session.refresh(profile)

        profile_public = ProfilePublic.from_orm(profile)
        return EnrollResponse(data=profile_public)

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi Database: {str(e)}")

@router.post("/search-face", response_model=SearchResponse)
async def search_face(
    request: SearchRequest,
    session: Session = Depends(get_session)
):


    vector = await get_embedding_from_api(request.image_base64)
    vector_str = str(list(vector))

    match_sql = text("SELECT * FROM match_users(:vec, :threshold, :count)")
    result = session.execute(
        match_sql,
        {"vec": vector_str, "threshold": 1, "count": 1}
    )
    found_user = result.fetchone()

    if not found_user:
        raise HTTPException(404, "Không tìm thấy sinh viên khớp khuôn mặt")

    profile_id = found_user.profile_id

    enroll_sql = text("""
        SELECT 1
        FROM enrollments
        WHERE course_id = :cid AND profile_id = :pid
    """)
    enrolled = session.execute(enroll_sql, {
        "cid": request.course_id,
        "pid": profile_id
    }).fetchone()

    if not enrolled:
        raise HTTPException(
            403,
            f"Sinh viên {found_user.name} ({found_user.student_id}) chưa đăng ký môn học này."
        )

    now  = datetime.now(timezone.utc)

    schedule_sql = text("""
        SELECT *
        FROM schedules
        WHERE course_id = :cid
          AND start_time <= :now
          AND end_time >= :now
        LIMIT 1
    """)
    schedule = session.execute(schedule_sql, {
        "cid": request.course_id,
        "now": now
    }).fetchone()

    if not schedule:
        raise HTTPException(
            400,
            "Hiện tại không có buổi học nào đang diễn ra."
        )

    late_threshold = schedule.start_time + timedelta(minutes=10)

    status = "present" if now <= late_threshold else "late"

    check_log = text("""
        SELECT 1
        FROM attendance_logs
        WHERE schedule_id = :sid AND profile_id = :pid
    """)
    exists = session.execute(check_log, {
        "sid": schedule.id,
        "pid": profile_id
    }).fetchone()

    if exists:
        raise HTTPException(409, "Sinh viên đã điểm danh buổi này rồi")

    try:
        insert_sql = text("""
            INSERT INTO attendance_logs (schedule_id, profile_id, status)
            VALUES (:sid, :pid, :status)
        """)
        session.execute(insert_sql, {
            "sid": schedule.id,
            "pid": profile_id,
            "status": status
        })
        session.commit()

    except Exception as e:
        session.rollback()
        raise HTTPException(500, f"Lỗi ghi điểm danh: {str(e)}")

    return SearchResponse(
        name=found_user.name,
        student_id=found_user.student_id,
        status=status,
        schedule_id=schedule.id
    )
@router.get("/health")
async def health_check():
    """
    Kiểm tra trạng thái của API và kết nối với Embedding API
    """
    embedding_status = "unknown"
    try:
        # Gọi thử health check của service AI
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(AI_HEALTH_ENDPOINT)
            if response.status_code == 200:
                embedding_status = "healthy"
            else:
                embedding_status = f"unhealthy_status_{response.status_code}"
    except Exception as e:
        embedding_status = f"unreachable ({str(e)})"

    return {
        "status": "healthy",
        "embedding_api_url": AI_SERVICE_BASE_URL,
        "embedding_api_status": embedding_status
    }