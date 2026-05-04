from collections import defaultdict

def make_group_key(r):
    f1, f2 = r["features"]

    return (
        r["case"],
        f1.get("type"),          # bolt vs nut 분리
        f1.get("material"),
        f2.get("material")       # mismatch 방향
    )

def group_similar(results):
    groups = defaultdict(list)

    for r in results:
        key = make_group_key(r)
        groups[key].append(r)

    return groups