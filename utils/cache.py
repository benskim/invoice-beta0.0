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
    return hashlib.md5(text.lower().strip().encode()).hexdigest()