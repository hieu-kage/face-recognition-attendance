# app/crud/enrollments.py
from sqlalchemy import text

from app.models import Profile, Enrollment, Course,Schedule,AttendanceLog
from app.schemas.profile import ProfileCreate


from fastapi import HTTPException, UploadFile
from sqlalchemy.dialects.postgresql import insert
import pandas as pd
import io
import httpx
import re
import joblib
from sqlmodel import Session, select, func, col
import math

from pathlib import Path
import traceback


from app.core.config import HF_OCR_API_URL
from app.schemas.enrollment import EnrollmentSearchFilter

# Model này được huấn luyện để nhận diện: 0:Other, 1:ID, 2:Fullname, 3:Surname, 4:Firstname
CURRENT_DIR = Path(__file__).resolve().parent
MODEL_PATH = CURRENT_DIR.parent / "ml_models" / "cell_classifier.pkl"  # Đổi tên model mới
ai_model = None

if MODEL_PATH.exists():
    try:
        ai_model = joblib.load(MODEL_PATH)
        print(f"--- AI Model loaded successfully from: {MODEL_PATH} ---")
    except Exception as e:
        print(f"--- Warning: Failed to load AI model: {e} ---")
else:
    print(f"--- Warning: AI model not found at {MODEL_PATH}. Tính năng đọc Excel thông minh sẽ không hoạt động. ---")



def extract_cell_features(cell_value):
    """
    Trích xuất đặc trưng từ nội dung của 1 ô Excel để đưa vào model.
    Input: Chuỗi văn bản (str)
    Output: List các chỉ số khớp với lúc train model.
    """
    val = str(cell_value).strip()

    # 1. Độ dài chuỗi
    length = len(val)

    # 2. Số lượng từ (khoảng trắng)
    word_count = len(val.split())

    # 3. Chứa số?
    has_digit = 1 if re.search(r'\d', val) else 0

    # 4. Bắt đầu bằng 'B' theo sau là số (Pattern mã SV PTIT)
    starts_with_B_digit = 1 if re.match(r'^B\d', val, re.IGNORECASE) else 0

    # 5. Viết hoa chữ cái đầu (Title Case)
    is_title = 1 if val.istitle() else 0

    # 6. Viết hoa toàn bộ (UPPER CASE)
    is_upper = 1 if val.isupper() else 0

    # 7. Tỉ lệ ký tự chữ cái (alpha ratio)
    alpha_count = sum(c.isalpha() for c in val)
    alpha_ratio = alpha_count / length if length > 0 else 0

    return [length, word_count, has_digit, starts_with_B_digit, is_title, is_upper, alpha_ratio]


# --- HÀM TRỢ GIÚP 1: XỬ LÝ FILE (LOGIC QUÉT HÀNG THÔNG MINH) ---

async def get_student_data_from_file(file: UploadFile):
    """
    Đọc file Excel/CSV, sử dụng AI để quét từng hàng (Row Scanning),
    tìm bộ đôi (ID + Tên) hợp lệ bất kể vị trí cột.
    """
    try:
        contents = await file.read()
        student_id_pattern = re.compile(r'^B\d{2}[A-Z]{2,6}\d{3}$', re.IGNORECASE)

        # 1. ĐỌC THÔ (Raw Read - Không Header)
        # Để không bị mất dữ liệu nếu file không có header hoặc header sai vị trí
        df = None
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(io.BytesIO(contents), header=None)
        else:
            # Xử lý encoding cho CSV
            try:
                df = pd.read_csv(io.BytesIO(contents), header=None, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(contents), header=None, encoding='tcvn-3')

        # Kiểm tra model
        if not ai_model:
            raise HTTPException(status_code=500, detail="AI Model chưa được load. Không thể xử lý file.")

        student_data = []

        # 2. DUYỆT TỪNG HÀNG (Row Iteration)
        for index, row in df.iterrows():
            # Biến lưu thông tin tìm được trong hàng này
            found_id = None
            found_fullname = None
            found_surname = None
            found_firstname = None

            # Duyệt qua từng ô trong hàng
            # (Giới hạn 20 cột đầu tiên để tối ưu hiệu năng nếu file có quá nhiều cột rỗng)
            for col_idx, cell_val in enumerate(row[:20]):
                val_str = str(cell_val).strip()

                # Bỏ qua ô rỗng hoặc quá ngắn (nhiễu)
                if len(val_str) < 2 or val_str.lower() == 'nan':
                    continue

                # Dự đoán loại ô bằng AI
                features = extract_cell_features(val_str)
                # Reshape cho đúng format input của sklearn: [[f1, f2...]]
                prediction = ai_model.predict([features])[0]

                # Logic gán giá trị (Lấy giá trị ĐẦU TIÊN tìm thấy khớp loại trong hàng)
                if prediction == 1:  # Label 1: ID
                    # Validate kỹ lại bằng Regex cho chắc chắn 100% là ID xịn
                    if student_id_pattern.match(val_str):
                        found_id = val_str.upper()

                elif prediction == 2 and not found_fullname:  # Label 2: Fullname
                    # Kiểm tra sơ bộ: Tên thường không có số (trừ trường hợp hãn hữu)
                    if not any(char.isdigit() for char in val_str):
                        found_fullname = val_str

                elif prediction == 3 and not found_surname:  # Label 3: Surname
                    if not any(char.isdigit() for char in val_str):
                        found_surname = val_str

                elif prediction == 4 and not found_firstname:  # Label 4: Firstname
                    if not any(char.isdigit() for char in val_str):
                        found_firstname = val_str

            # 3. TỔNG HỢP DỮ LIỆU SAU KHI QUÉT XONG 1 HÀNG
            if found_id:
                final_name = ""

                # Ưu tiên lấy Fullname gộp sẵn
                if found_fullname:
                    final_name = found_fullname
                # Nếu không có Fullname, thử ghép Họ + Tên
                elif found_surname and found_firstname:
                    final_name = f"{found_surname} {found_firstname}"

                # Nếu tìm được đủ bộ ID + Tên hợp lệ -> Lưu lại
                if final_name:
                    # Chuẩn hóa tên (Title Case: Nguyễn Văn A)
                    final_name = " ".join(final_name.split()).title()

                    student_data.append({
                        "id": found_id,
                        "name": final_name
                    })

        if not student_data:
            raise HTTPException(status_code=400, detail="Không tìm thấy dữ liệu sinh viên hợp lệ nào trong file.")

        return student_data

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Lỗi xử lý file: {str(e)}")


# XỬ LÝ ẢNH (Giữ nguyên) ---
async def get_student_ids_from_image(file: UploadFile):

    if not HF_OCR_API_URL:
        return ["B22DCPT090", "B21DCAT007"]
    try:
        contents = await file.read()
        files = {'image': (file.filename, contents, file.content_type)}
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(HF_OCR_API_URL, files=files)
            response.raise_for_status()
            data = response.json()
            if not data.get('success') or 'student_ids' not in data:
                raise HTTPException(status_code=502, detail="OCR service error")
            return data['student_ids']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling OCR: {e}")


#HÀM CRUD CHÍNH (Logic Get-or-Create & Enroll) ---

async def enroll_students_from_file(db: Session, course_id: int, file: UploadFile):

    student_data = []
    file_type = file.content_type

    await file.seek(0)

    if 'image' in file_type:
        ocr_ids = await get_student_ids_from_image(file)
        student_data = [{"id": sid, "name": ""} for sid in ocr_ids]

    elif 'csv' in file_type or 'sheet' in file_type or 'excel' in file_type:
        student_data = await get_student_data_from_file(file)

    else:
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file .csv, .xls, .xlsx và ảnh (.png, .jpg)")

    if not student_data:
        raise HTTPException(status_code=404, detail="Không tìm thấy MSSV nào.")

    all_ids_in_file = list(set(item['id'] for item in student_data))
    data_map_by_id = {item['id']: item for item in student_data}

    # 1. Tìm profile đã có
    statement = select(Profile).where(Profile.student_id.in_(all_ids_in_file))
    found_profiles = db.exec(statement).all()
    found_ids = set(p.student_id for p in found_profiles)

    # 2. Tạo profile mới
    new_ids_to_create = set(all_ids_in_file) - found_ids
    new_profiles = []

    for new_id in new_ids_to_create:
        student_name = data_map_by_id[new_id]['name']
        new_profile = Profile(student_id=new_id, name=student_name)
        db.add(new_profile)
        new_profiles.append(new_profile)

    if new_profiles:
        try:
            db.commit()
            for p in new_profiles:
                db.refresh(p)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Lỗi tạo profile mới: {e}")

    # 3. Lấy danh sách profile_id sẽ được ghi danh cho lớp
    final_profile_id_map = {p.student_id: p.id for p in found_profiles}
    final_profile_id_map.update({p.student_id: p.id for p in new_profiles})

    # final_profile_id_map = {
    #     "B2012345": 101,
    #     "B2012346": 102,
    #     "B2012347": 103,
    # }
    enrollment_dicts = []
    for sid in all_ids_in_file:
        pid = final_profile_id_map.get(sid) # Lấy id của bảng Profile
        if pid:
            enrollment_dicts.append({'profile_id': pid, 'course_id': course_id})

    if not enrollment_dicts:
        raise HTTPException(status_code=400, detail="Không có sinh viên hợp lệ để ghi danh.")

    try:
        stmt = insert(Enrollment).values(enrollment_dicts).on_conflict_do_nothing(
            index_elements=['profile_id', 'course_id']
        )
        db.execute(stmt)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi ghi danh: {e}")

    message = f"Ghi danh thành công {len(enrollment_dicts)} sinh viên."
    if new_profiles:
        message += f" Đã tạo {len(new_profiles)} profile mới."

    return {"success": True, "message": message}


async def get_enrollments_by_course(db: Session, course_id: int):

    statement = (
        select(Enrollment, Profile)
        .join(Profile, Enrollment.profile_id == Profile.id)
        .where(Enrollment.course_id == course_id)
    )

    results = db.exec(statement).all()

    enrollment_list = []
    for enrollment, profile in results:
        enrollment_list.append({
            "enrollment_id": enrollment.id,
            "student_id": profile.student_id,
            "student_name": profile.name,
            "profile_id": profile.id,
            "joined_at": enrollment.joined_at
        })

    return enrollment_list


def search_enrollments(db: Session, filter: EnrollmentSearchFilter):
    statement = (
        select(Enrollment, Profile)
        .join(Profile, Enrollment.profile_id == Profile.id)
    )

    if filter.course_id:
        statement = statement.where(Enrollment.course_id == filter.course_id)

    if filter.student_id:
        statement = statement.where(Profile.student_id.ilike(f"%{filter.student_id}%"))

    if filter.student_name:
        statement = statement.where(Profile.name.ilike(f"%{filter.student_name}%"))

    total_count_stmt = select(func.count()).select_from(statement.subquery())
    total_rows = db.exec(total_count_stmt).one()

    offset = (filter.page - 1) * filter.page_size
    statement = statement.offset(offset).limit(filter.page_size)
    results = db.exec(statement).all()


    profile_ids = [p.id for (_, p) in results]


    if filter.course_id:

        schedule_ids = db.exec(
            select(Schedule.id).where(Schedule.course_id == filter.course_id)
        ).all()


        schedule_ids = list(schedule_ids)
    else:
        schedule_ids = []

    total_sessions = len(schedule_ids)


    attendance_map = {}
    if total_sessions > 0 and profile_ids:
        rows = db.exec(
            select(
                AttendanceLog.profile_id,
                func.count().label("cnt")
            )
            .where(AttendanceLog.profile_id.in_(profile_ids))
            .where(AttendanceLog.schedule_id.in_(schedule_ids))
            .where(AttendanceLog.status.in_(["present", "late"]))
            .group_by(AttendanceLog.profile_id)
        ).all()

        attendance_map = {pid: cnt for (pid, cnt) in rows}

    data = []
    for enrollment, profile in results:
        attended_count = attendance_map.get(profile.id, 0)
        attendance_rate = (
            round(attended_count / total_sessions * 100, 1)
            if total_sessions > 0 else 0.0
        )

        data.append({
            "enrollment_id": enrollment.id,
            "course_id": enrollment.course_id,
            "student_id": profile.student_id,
            "student_name": profile.name,
            "profile_id": profile.id,

            "attended_count": attended_count,
            "total_sessions": total_sessions,
            "attendance_rate": attendance_rate
        })

    return {
        "success": True,
        "total": total_rows,
        "page": filter.page,
        "page_size": filter.page_size,
        "total_pages": math.ceil(total_rows / filter.page_size),
        "data": data
    }



def add_student_to_course(db: Session, course_id: int, profile_data: ProfileCreate):
    existing = db.exec(select(Profile).where(Profile.student_id == profile_data.student_id)).first()

    if existing:
        profile = existing
    else:
        profile = Profile(name=profile_data.name, student_id=profile_data.student_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # 3. Thêm vào course (nếu chưa có)
    enrollment_exists = db.exec(
        select(Enrollment).where(
            Enrollment.course_id == course_id,
            Enrollment.profile_id == profile.id
        )
    ).first()

    if not enrollment_exists:
        enrollment = Enrollment(course_id=course_id, profile_id=profile.id)
        db.add(enrollment)
        db.commit()

    return {
        "message": "Student enrolled successfully",
        "profile_id": profile.id
    }
