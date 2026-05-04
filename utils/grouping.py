from collections import defaultdict

def group_similar(results):
    groups = defaultdict(list)

    for r in results:
        key = (r["case"], r["best"])
        groups[key].append(r)

    return groups