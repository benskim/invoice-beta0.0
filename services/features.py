from utils.cache import load_cache, save_cache, make_key
from services.parsing import extract_features as parse_extract_features

CACHE = load_cache()

def extract_features(text):
    # 🔥 방어 코드
    if isinstance(text, dict):
        text = text.get("description", "")

    if text is None:
        return {
            "type": None,
            "material": None,
            "size": None,
            "etc": []
        }

    if not isinstance(text, str):
        text = str(text)

    # logic
    key = make_key(text)

    if key in CACHE:
        return CACHE[key]["features"]

    features = parse_extract_features(text)

    CACHE[key] = {
        "raw": text,
        "features": features
    }

    save_cache(CACHE)

    return features