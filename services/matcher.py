from services.features import extract_features

def compute_score(inv, po):
    f1 = extract_features(inv)
    f2 = extract_features(po)

    score = 0
    total = 3

    for k in ["type", "material", "size"]:
        if f1.get(k) == f2.get(k):
            score += 1

    return round(score / total, 2)

def get_candidates(inv, po_list):
    scored = [(po, compute_score(inv, po)) for po in po_list]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:3]