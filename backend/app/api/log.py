
from fastapi import APIRouter, HTTPException
from app.core.config import supabase_client

router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)
@router.get("/logs")
async def get_attendance_logs():
    try:
        query = supabase_client.table('attendance_logs') \
                        .select('created_at, users(name, student_id)') \
                        .order('created_at', desc=True) \
                        .limit(50)
        data = query.execute()
        return {"success": True, "logs": data.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))