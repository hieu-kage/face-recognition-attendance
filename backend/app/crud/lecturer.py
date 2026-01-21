# app/crud/lecturers.py
from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from app.models.profile import Profile,Lecturer
from app.schemas.lecturer import LecturerCreate


def create_lecturer(db: Session, lecturer: LecturerCreate):
    """
    Tạo giảng viên: Tạo 1 Profile VÀ 1 Lecturer liên kết
    """
    try:
        # 1. Tạo Profile
        new_profile = Profile(
            name=lecturer.name,
            email=lecturer.email,
            role='lecturer'
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)

        new_lecturer = Lecturer(profile_id=new_profile.id)
        db.add(new_lecturer)
        db.commit()
        db.refresh(new_lecturer)

        return {"id": new_lecturer.id, "name": new_profile.name}

    except IntegrityError:  # Bắt lỗi email/sdt trùng
        db.rollback()
        raise HTTPException(status_code=409, detail="Email đã tồn tại")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def get_all_lecturers(db: Session):
    """
    Lấy danh sách (ID giảng viên, Tên) để điền vào dropdown
    """
    statement = select(Lecturer.id, Profile.name).join(
        Profile, Lecturer.profile_id == Profile.id
    )
    results = db.exec(statement).all()

    # Chuyển đổi [Row(id=1, name='A')] thành [{id: 1, name: 'A'}]
    return [{"id": row.id, "name": row.name} for row in results]