def classify_case(f1, f2):
    if f1.get("material") != f2.get("material"):
        return "HIGH_RISK", "Material mismatch"
    if f1.get("size") != f2.get("size"):
        return "REVIEW", "Size mismatch"
    return "SAFE", "Naming variation"

def decide(case, score):
    if score < 0.7:
        return "REVIEW"

    if case == "HIGH_RISK":
        return "REJECT"

    return "AUTO"