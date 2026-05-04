THRESHOLD = 0.85

def classify_case(f1, f2):
    if f1.get("material") != f2.get("material"):
        return "HIGH_RISK", "Material mismatch"
    if f1.get("size") != f2.get("size"):
        return "REVIEW", "Size mismatch"
    return "SAFE", "Naming variation"

def pick_best(candidates):
    if not candidates:
        return None

    return candidates[0]


def needs_review(best, threshold=THRESHOLD):
    if not best:
        return True

    return best["score"] < threshold


def decide(case, score):
    if score < THRESHOLD:
        return "REVIEW"

    if case == "HIGH_RISK":
        return "REVIEW"

    return "AUTO"

def confidence_label(score):
    if score > 0.9:
        return "🔥 High"
    elif score > 0.75:
        return "👍 Medium"
    else:
        return "⚠️ Low"