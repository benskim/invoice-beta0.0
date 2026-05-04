from supabase import create_client
from dotenv import load_dotenv
from os import getenv

# .env 파일 로드
load_dotenv()
# 환경 변수에서 키 읽기
url = getenv("SUPABASE_URL")
key = getenv("SUPABASE_KEY")

supabase = create_client(url, key)

def save_feedback(data):
    supabase.table("feedback").insert(data).execute()