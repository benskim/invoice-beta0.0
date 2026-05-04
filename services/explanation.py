def explain_mismatch(f1, f2):
    reasons = []

    if f1.get("type") != f2.get("type"):
        reasons.append("TYPE_MISMATCH")

    if f1.get("material") != f2.get("material"):
        reasons.append("MATERIAL_MISMATCH")

    if f1.get("size") != f2.get("size"):
        reasons.append("SIZE_MISMATCH")

    if not reasons:
        reasons.append("UNKNOWN")

    return reasons


def suggest_action(reasons, score):
    actions = []

    if "TYPE_MISMATCH" in reasons:
        actions.append("🔴 다른 품목 (bolt vs nut) → 다른 PO 선택")

    if "MATERIAL_MISMATCH" in reasons:
        actions.append("🟡 소재 불일치 (SS vs steel) → 유사 후보 확인")

    if "SIZE_MISMATCH" in reasons:
        actions.append("🟠 사이즈 불일치 (M8 vs M10) → 수량/규격 확인")

    if score < 0.5:
        actions.append("⚠️ 매칭 신뢰도 낮음 → 수동 검토 필요")

    if not actions:
        actions.append("✅ 문제 없음 → 자동 승인 가능")

    return actions