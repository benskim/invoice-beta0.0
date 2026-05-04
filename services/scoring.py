def compute_score(f1, f2):
    score = 0.0
    total = 0.0

    # TYPE
    if f1["type"] and f2["type"]:
        total += 0.3
        if f1["type"] == f2["type"]:
            score += 0.3

    # MATERIAL
    if f1["material"] and f2["material"]:
        total += 0.3
        if f1["material"] == f2["material"]:
            score += 0.2

    # SIZE
    if f1["size"] and f2["size"]:
        total += 0.2
        if f1["size"] == f2["size"]:
            score += 0.1

    if total == 0:
        return 0

    return round(score / total, 2)