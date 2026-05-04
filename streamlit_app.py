import streamlit as st
from services.parsing import parse_invoice
from services.matcher import get_candidates
from services.features import extract_features
from services.decision import classify_case
from services.supabase_client import save_feedback
from utils.grouping import group_similar
import time


# 세션 상태 초기화 (앱 시작 시 한 번만 실행)
if "results" not in st.session_state:
    st.session_state.results = None
# if "mode" not in st.session_state:
#     st.session_state.mode = "summary"
if "idx" not in st.session_state:
    st.session_state.idx = 0

# 🔹 샘플 PO 데이터
PO_DATA = [
    "M8 stainless bolt",
    "Hex bolt 8mm steel",
    "Nut M8 stainless",
    "Washer 8mm"
]

# 🎯 UI
st.title("Invoice → PO Matching (Gemini MVP)")
file = st.file_uploader("Upload Invoice", type=["txt", "pdf","xlsx"])

# -------------------------
# 분석
# -------------------------
if file and st.button("Analyze"):
    try:
        raw_data = file.read()
        text = raw_data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw_data.decode("cp949") # 한국어 윈도우 환경 대응
        except:
            st.error("파일 인코딩을 확인할 수 없습니다. (UTF-8 또는 CP949 권장)")
            st.stop()

    st.subheader("🤖 Processing...")
    # [추가 아이디어] Progress Bar 적용
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 무거운 작업(AI 분석)에 캐싱 적용
    # 동일한 파일 내용을 넣으면 API를 다시 호출하지 않고 저장된 결과를 반환합니다.
    @st.cache_data(show_spinner=False)
    def cached_parse_invoice(text):
        return parse_invoice(text)
    items = cached_parse_invoice(text)

    total = len(items)
    results = []

    for i, item in enumerate(items):
        inv = item["description"]

        candidates = get_candidates(inv, PO_DATA)
        best, score = candidates[0]

        f1 = extract_features(inv)
        f2 = extract_features(best)

        case, hint = classify_case(f1, f2)

        results.append({
            "invoice": inv,
            "candidates": candidates,
            "best": best,
            "score": score,
            "case": case,
            "hint": hint,
            "features": (f1, f2)
        })

        # Progress 업데이트
        progress_bar.progress((i + 1) / total)
        status_text.text(f"분석 중... ({i+1}/{total})")

    st.session_state.results = results
    st.session_state.idx = 0
    st.session_state.decisions = []

    status_text.text("✅ 분석 완료!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

# -------------------------
# Summary
# -------------------------
if st.session_state.results:
    results = st.session_state.results

    safe = [r for r in results if r["case"] == "SAFE"]
    issues = [r for r in results if r["case"] != "SAFE"]

    st.subheader("📊 Summary")
    st.write(f"✅ Auto: {len(safe)}")
    st.write(f"⚠️ Issues: {len(issues)}")

    show_auto = st.checkbox("Show Auto Matches")

    if show_auto:
        for r in safe:
            st.write(f"{r['invoice']} → {r['best']}")

    if st.button("👉 Review Issues"):
        st.session_state.mode = "focus"

# -------------------------
# Focus Mode
# -------------------------
if st.session_state.get("mode") == "focus":
    issues = [r for r in results if r["case"] != "SAFE"] #st.session_state.results

    # -------------------------
    # Batch 그룹
    # -------------------------
    groups = group_similar(issues)

    st.subheader("⚡ Batch Actions")

    for idx, ((case, best), items) in enumerate(groups.items()):
        if len(items) > 1:
            with st.expander(f"{case} → {best} ({len(items)} items)"):
                for i in items:
                    st.write(i["invoice"])

                if st.button(f"Approve All {best}", key=f"btn_{idx}_{best}"):
                    for i in items:
                        save_feedback({
                            "invoice": i["invoice"],
                            "selected": best,
                            "case": case
                        })
                    st.success("Batch Applied")

    # -------------------------
    # Single 처리
    # -------------------------
    idx = st.session_state.idx

    if idx < len(issues):
        r = issues[idx]

        st.markdown("---")
        st.write(f"### {r['invoice']}")

        options = [f"{po} ({score})" for po, score in r["candidates"]]

        sel = st.selectbox("Select", range(len(options)), format_func=lambda x: options[x])

        selected_po = r["candidates"][sel][0]

        # 1. Invoice 특징(f1)은 이미 분석 단계에서 만든 걸 그대로 가져옵니다.
        f1 = r["features"][0]
        # 2. PO 특징(f2)은 사용자가 선택한 게 '최적(best)'과 같다면 재사용하고, 
        #    다른 걸 골랐을 때만 새로 계산합니다.
        selected_po = r["candidates"][sel][0]
        if selected_po == r["best"]:
            f2 = r["features"][1] # 저장된 값 재사용
        else:
            f2 = extract_features(selected_po) # 새로 고른 것만 계산

        st.write("### 🔍 Why")
        for k in f1:
            st.write(f"{k}: {f1[k]} vs {f2[k]}")

        col1, col2 = st.columns(2)

        if col1.button("Accept"):
            save_feedback({
                "invoice": r["invoice"],
                "selected": selected_po,
                "case": r["case"]
            })
            st.session_state.idx += 1
            st.rerun()

        if col2.button("Reject"):
            save_feedback({
                "invoice": r["invoice"],
                "selected": "REJECT",
                "case": r["case"]
            })
            st.session_state.idx += 1
            st.rerun()

    else:
        st.success("🎉 Done")


    # # 🔥 로그 확인
    # st.subheader("🧪 Gemini Raw Output")
    # st.code(raw)

    # # 🔥 JSON 정리
    # raw = raw.replace("```json", "").replace("```", "").strip()

    # try:
    #     return json.loads(raw)
    # except:
    #     st.error("❌ JSON parsing 실패")
    #     return []



# if file:
#     st.subheader("📄 Raw Text")
#     st.text(text)

#     # results = process_invoice(text)
#     # if results:
#     #     st.subheader("✅ Matching Result")
#     #     st.write(results)
#     # else:
#     #     st.warning("결과 없음")

#     st.subheader("🎯 Final Decision")

#     final_results = []

#     for item in results:
#         best = pick_best(item["candidates"])
#         review_flag = needs_review(best)

#         result = {
#             "invoice": item["invoice"],
#             "best_match": best["po"],
#             "score": best["score"],
#             "needs_review": review_flag
#         }

#         final_results.append(result)

#         # UI 출력
#         st.write(result)

#         # 🔥 human review UI
#         if review_flag:
#             st.warning("⚠️ Needs Human Review")

#             options = [c["po"] for c in item["candidates"]]

#             selected = st.selectbox(
#                 f"Select correct match for: {item['invoice']}",
#                 options,
#                 key=item["invoice"]
#             )

#             st.write("✅ Selected:", selected)    

    # import pandas as pd

    # if "log" not in st.session_state:
    #     st.session_state.log = []

    # for r in final_results:
    #     st.session_state.log.append(r)

    # if st.button("💾 Save Log"):
    #     df = pd.DataFrame(st.session_state.log)
    #     df.to_csv("match_log.csv", index=False)
    #     st.success("Saved to match_log.csv")