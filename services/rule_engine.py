import json
import os

RULE_FILE = "data/rules.json"

def load_rules():
    if os.path.exists(RULE_FILE):
        try:
            with open(RULE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {"material": {}, "size": {}, "type": {}}
    return {"material": {}, "size": {}, "type": {}}


def save_rules(rules):
    with open(RULE_FILE, "w") as f:
        json.dump(rules, f, indent=2)


def apply_rules(f):
    rules = load_rules()

    for k in ["material", "size", "type"]:
        val = f.get(k)
        if val in rules.get(k, {}):
            f[k] = rules[k][val]

    return f


def update_rules(f1, f2):
    rules = load_rules()

    for k in ["material", "size", "type"]:
        v1 = f1.get(k)
        v2 = f2.get(k)

        if v1 and v2 and v1 != v2:
            # 중복 덮어쓰기 방지
            if v1 not in rules[k]:
                rules[k][v1] = v2

    save_rules(rules)