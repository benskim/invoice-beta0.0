import streamlit as st
from services.parsing import parse_invoice
from services.matching import match_item
from services.decision import pick_best, decide
from services.features import extract_features
from services.decision import classify_case
from services.supabase_client import save_feedback
from utils.grouping import group_similar
from services.rule_engine import update_rules
from services.decision import confidence_label
from services.explanation import explain_mismatch,suggest_action
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

        r = match_item(inv, PO_DATA)
        best = pick_best(r["candidates"]) 
        if not best:
            results.append({
                "invoice": r["invoice"],
                "error": "NO_CANDIDATE"
            })
            continue

        case, hint = classify_case(r["features"], best["features"])  # 기존 함수
        decision = decide(case, best["score"])

        results.append({
            "invoice": r["invoice"],
            "features": r["features"],
            "candidates": r["candidates"],
            "best": best["po"],
            "score": best["score"],
            "case": case,
            "decision": decision
        })
    

        # candidates = get_candidates(inv, PO_DATA)
        # best, score = candidates[0]
        # f1 = extract_features(inv)
        # f2 = extract_features(best)

        # case, hint = classify_case(f1, f2)

        # results.append({
        #     "invoice": inv,
        #     "candidates": candidates,
        #     "best": best,
        #     "score": score,
        #     "case": case,
        #     "hint": hint,
        #     "features": (f1, f2)
        # })

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
            label = confidence_label(r["score"])
            st.success(f"✅ {r['invoice']} → {r['best']} ({r['score']}) {label}")
            st.caption("자동 승인됨 (높은 유사도)")            

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
    for idx, (key, items) in enumerate(groups.items()):
        case, type_, mat1, mat2 = key

        # if len(items) < 2:
        #     continue

        with st.expander(
            f"{case} | {type_} | {mat1} → {mat2} ({len(items)} items)"
        ):
            for i in items:
                st.write(i["invoice"])

            # ⭐ best는 그룹에서 하나 대표로 가져옴
            best = items[0]["best"]

            if st.button(
                f"Approve All → {best}",
                key=f"btn_{idx}_{type_}_{mat1}_{mat2}"
            ):
                for i in items:
                    save_feedback({
                        "invoice": i["invoice"],
                        "selected": best,
                        "case": case
                    })
                    update_rules(i["features"], i["candidates"][0]["features"])

                st.success("Batch Applied")

    # -------------------------
    # Single 처리 (강화 UI)
    # -------------------------
    idx = st.session_state.idx

    if idx >= len(issues):
        st.success("🎉 Done")
        st.stop()

    r = issues[idx]

    st.markdown("---")
    st.write(f"### {r['invoice']} → {r['best']} ({r['score']})")

    # 후보 표시 (dict 구조 기준)
    options = [f"{c['po']} ({c['score']})" for c in r["candidates"]]

    sel = st.selectbox(
        "Select best match",
        range(len(options)),
        format_func=lambda x: options[x]
    )

    selected = r["candidates"][sel]
    selected_po = selected["po"]

    # feature 가져오기
    f1 = r["features"]

    if selected_po == r["best"]:
        f2 = r["candidates"][0]["features"]
    else:
        f2 = extract_features(selected_po)

    # -------------------------
    # 🔍 WHY (핵심)
    # -------------------------
    st.write("### 🔍 Why mismatch?")

    reasons = explain_mismatch(f1, f2)

    for rsn in reasons:
        st.warning(rsn)

    # feature 비교 시각화
    with st.expander("📊 Feature Compare"):
        for k in f1:
            st.write(f"{k}: {f1.get(k)} vs {f2.get(k)}")

    # -------------------------
    # 🎯 ACTION (핵심)
    # -------------------------
    st.write("### 🎯 Recommended Action")

    actions = suggest_action(reasons, selected["score"])

    for a in actions:
        st.info(a)

    # -------------------------
    # 선택 버튼
    # -------------------------
    col1, col2 = st.columns(2)

    if col1.button("✅ Accept"):
        save_feedback({
            "invoice": r["invoice"],
            "selected": selected_po,
            "case": r["case"]
        })
        update_rules(f1, f2)
        st.session_state.idx += 1
        st.rerun()

    if col2.button("❌ Reject"):
        save_feedback({
            "invoice": r["invoice"],
            "selected": "REJECT",
            "case": r["case"]
        })
        st.session_state.idx += 1
        st.rerun()