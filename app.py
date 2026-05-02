import streamlit as st
import google.generativeai as genai
import json

# 🔑 API KEY (처음엔 그냥 하드코딩 추천)
genai.configure(api_key="AIzaSyCJxQO1OTpIK09RisxDn5pNUS16ti-U8SQ")

model = genai.GenerativeModel("gemini-2.5-flash")
# 🔥 후보 중 최고 선택
def pick_best(candidates):
    return sorted(candidates, key=lambda x: x["score"], reverse=True)[0]

# 🔥 threshold 판단
def needs_review(best, threshold=0.75):
    return best["score"] < threshold

# 🔹 샘플 PO 데이터
PO_DATA = [
    "M8 stainless bolt",
    "Hex bolt 8mm steel",
    "Nut M8 stainless",
    "Washer 8mm"
]

# 🔥 Gemini parsing + matching
def process_invoice(text):
    prompt = f'''
You are an expert in invoice processing.

PO LIST:
{PO_DATA}

TASK:
1. Extract ALL line items from the invoice
2. For each item, return TOP 3 candidates FROM THE PO LIST

STRICT RULES:
- Only select from PO LIST (do not invent new items)
- Do NOT skip any line
- Do NOT merge lines
- Keep original invoice wording
- Match based on material, size, and type (e.g. SS = stainless)

OUTPUT RULE:
- Return exactly 3 candidates for each item
- If not sure, still return the closest 3

RETURN ONLY JSON:

[
  {{
    "invoice": "...",
    "candidates": [
      {{"po": "...", "score": 0.9}},
      {{"po": "...", "score": 0.7}},
      {{"po": "...", "score": 0.5}}
    ]
  }}
]

SCORING RULE:
- 0.9~1.0 = exact match (material + size + type)
- 0.7~0.9 = similar
- below 0.7 = weak

Invoice:
{text}
'''
    try:
        res = model.generate_content(prompt)
        raw = res.text
    except Exception as e:
        st.error(f"Gemini API Error: {e}")
        return []

    # 🔥 로그 확인
    st.subheader("🧪 Gemini Raw Output")
    st.code(raw)

    # 🔥 JSON 정리
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except:
        st.error("❌ JSON parsing 실패")
        return []

# 🎯 UI
st.title("Invoice → PO Matching (Gemini MVP)")

uploaded_file = st.file_uploader("Upload Invoice (.txt 추천)")

if uploaded_file:
    try:
        text = uploaded_file.read().decode("utf-8")
    except:
        st.error("파일 읽기 실패 (UTF-8 아님)")
        st.stop()

    st.subheader("📄 Raw Text")
    st.text(text)

    st.subheader("🤖 Processing...")
    results = process_invoice(text)

    # if results:
    #     st.subheader("✅ Matching Result")
    #     st.write(results)
    # else:
    #     st.warning("결과 없음")

    st.subheader("🎯 Final Decision")

    final_results = []

    for item in results:
        best = pick_best(item["candidates"])
        review_flag = needs_review(best)

        result = {
            "invoice": item["invoice"],
            "best_match": best["po"],
            "score": best["score"],
            "needs_review": review_flag
        }

        final_results.append(result)

        # UI 출력
        st.write(result)

        # 🔥 human review UI
        if review_flag:
            st.warning("⚠️ Needs Human Review")

            options = [c["po"] for c in item["candidates"]]

            selected = st.selectbox(
                f"Select correct match for: {item['invoice']}",
                options,
                key=item["invoice"]
            )

            st.write("✅ Selected:", selected)    

    import pandas as pd

    if "log" not in st.session_state:
        st.session_state.log = []

    for r in final_results:
        st.session_state.log.append(r)

    if st.button("💾 Save Log"):
        df = pd.DataFrame(st.session_state.log)
        df.to_csv("match_log.csv", index=False)
        st.success("Saved to match_log.csv")