from services.features import extract_features
from services.scoring import compute_score

def match_item(inv, po_list):
    
    f1 = extract_features(inv)

    results = []

    for po in po_list:
        f2 = extract_features(po)
        s = compute_score(f1, f2)

        results.append({
            "po": po,
            "score": s,
            "features": f2
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "invoice": inv,
        "features": f1,
        "candidates": results[:3]
    }

# def compute_score(inv, po):
#     f1 = extract_features(inv)
#     f2 = extract_features(po)

#     score = 0
#     total = 3

#     for k in ["type", "material", "size"]:
#         if f1.get(k) == f2.get(k):
#             score += 1

#     return round(score / total, 2)

# def get_candidates(inv, po_list):
#     scored = [(po, compute_score(inv, po)) for po in po_list]
#     scored.sort(key=lambda x: x[1], reverse=True)
#     return scored[:3]