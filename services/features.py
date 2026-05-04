from utils.cache import load_cache, save_cache, make_key
from services.parsing import extract_features_llm

CACHE = load_cache()

def extract_features(text):
    key = make_key(text)

    if key in CACHE:
        return CACHE[key]["features"]

    features = extract_features_llm(text)

    CACHE[key] = {
        "raw": text,
        "features": features
    }

    save_cache(CACHE)

    return features