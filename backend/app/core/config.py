# config

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
HF_OCR_API_URL=""
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL (chuỗi kết nối CSDL) không được tìm thấy")

supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
HF_API_URL = os.environ.get("HF_API_URL")