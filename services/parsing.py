import google.genai as genai
import json
from dotenv import load_dotenv
from os import getenv
import streamlit as st

# .env 파일 로드
load_dotenv()
# 환경 변수에서 키 읽기
api_key = getenv("GOOGLE_API_KEY")

# # 설정 적용
# genai.configure(api_key=api_key)
# 
# @st.cache_resource
# def load_model():
#     return genai.GenerativeModel("gemini-2.5-flash")
# model = load_model()

# 1. 내부용 클라이언트 생성 (외부 노출 X)
@st.cache_resource
def _get_client():
    return genai.Client(api_key=api_key)

# 2. 외부에서는 이 함수만 호출함
def get_ai_response(prompt: str, model_id: str = "gemini-2.5-flash"):
    """
    app.py에서 호출할 유일한 진입점입니다.
    모든 SDK 관련 로직은 이 함수 내부에 갇혀 있습니다.
    """
    client = _get_client()
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI 서비스 에러: {e}"

# # 🔥 후보 중 최고 선택
# def pick_best(candidates):
#     return sorted(candidates, key=lambda x: x["score"], reverse=True)[0]

# # 🔥 threshold 판단
# def needs_review(best, threshold=0.75):
#     return best["score"] < threshold

def parse_invoice(text):
    prompt = f"""
You are an invoice expert.

TASK:
1. Extract ALL line items from invoice.

Return JSON:
[
  {"line number": "...",
     "description": "...",
     "unit price": "...", 
     "quantity": "...", 
     "amount": "...", 
     "tax": "...", 
     "discount": "...", 
     "etc" : "..." },
 {"line number": "...",
     "description": "...",
     "unit price": "...", 
     "quantity": "...", 
     "amount": "...", 
     "tax": "...", 
     "discount": "...", 
     "etc" : "..." }, 
     ...  
]

Invoice:
{text}
"""
    raw_txt = get_ai_response(prompt)
    # model.generate_content(prompt)

    if raw_txt is not None:
        return json.loads(raw_txt)
    else:
        return [{}]
    # try:
    #     return json.loads(raw_txt)
    # except:
    #     return []

def extract_features_llm(text):
    prompt = f"""
Extract structured attributes.

Return JSON:
{{
  "type": "...",
  "material": "...",
  "size": "...",
  "etc": []
}}

Item:
{text}
"""
    raw_txt = get_ai_response(prompt)

    # 🔥 디버깅
    print("RAW:", raw_txt)
    if raw_txt:
        raw = raw_txt.replace("```json", "").replace("```", "").strip()        
        return json.loads(raw)
    return {}


# # 🔥 Gemini parsing + matching
# def process_invoice(text):
#     prompt = f'''
# You are an expert in invoice processing.

# PO LIST:
# {PO_DATA}

# TASK:
# 1. Extract ALL line items from the invoice
# 2. For each item, return TOP 3 candidates FROM THE PO LIST

# STRICT RULES:
# - Only select from PO LIST (do not invent new items)
# - Do NOT skip any line
# - Do NOT merge lines
# - Keep original invoice wording
# - Match based on material, size, and type (e.g. SS = stainless)

# OUTPUT RULE:
# - Return exactly 3 candidates for each item
# - If not sure, still return the closest 3

# RETURN ONLY JSON:

# [
#   {{
#     "invoice": "...",
#     "candidates": [
#       {{"po": "...", "score": 0.9}},
#       {{"po": "...", "score": 0.7}},
#       {{"po": "...", "score": 0.5}}
#     ]
#   }}
# ]

# SCORING RULE:
# - 0.9~1.0 = exact match (material + size + type)
# - 0.7~0.9 = similar
# - below 0.7 = weak

# Invoice:
# {text}
# '''
#     try:
#         res = model.generate_content(prompt)
#         raw = res.text
#     except Exception as e:
#         st.error(f"Gemini API Error: {e}")
#         return []
