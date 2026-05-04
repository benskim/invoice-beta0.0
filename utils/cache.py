import json, os, hashlib

CACHE_FILE = "data/feature_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def make_key(text):

    if isinstance(text, (dict, list)):
        normalized = json.dumps(text, sort_keys=True, ensure_ascii=False)

    elif isinstance(text, bytes):
        normalized = text.decode("utf-8", errors="ignore")

    elif text is None:
        normalized = ""

    else:
        normalized = str(text)

    # 🔥 여기 중요 (string 보장)
    normalized = normalized.lower().strip()

    return hashlib.md5(normalized.encode()).hexdigest()