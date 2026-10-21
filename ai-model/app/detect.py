import re

_VI_WORDS = {
    "và",
    "của",
    "là",
    "những",
    "không",
    "các",
    "một",
    "trong",
    "cho",
    "được",
    "này",
    "với",
    "xin",
    "chào",
}
_EN_WORDS = {"the", "and", "hello", "thank", "you", "goodbye", "good", "morning"}
_TOKEN = re.compile(r"\w+", re.UNICODE)


def detect_language(text: str) -> dict:
    """Cheap language guess used until a trained identifier is loaded.

    Latin-script ethnic languages share Vietnamese letters, so this function
    refuses to guess them. Cham script is the one case decided from characters.
    """
    if any("\uAA00" <= char <= "\uAA5F" for char in text):
        return {"language": "cjm", "confidence": 0.99, "method": "script"}
    tokens = [token.casefold() for token in _TOKEN.findall(text)]
    if not tokens:
        return {"language": "und", "confidence": 0.0, "method": "empty"}
    vi_hits = sum(token in _VI_WORDS for token in tokens)
    en_hits = sum(token in _EN_WORDS for token in tokens)
    if vi_hits >= 1 and vi_hits >= en_hits:
        return {
            "language": "vi",
            "confidence": min(0.55 + 0.1 * vi_hits, 0.9),
            "method": "lexicon",
        }
    if en_hits >= 1 and en_hits > vi_hits:
        return {"language": "en", "confidence": 0.6, "method": "lexicon"}
    return {"language": "und", "confidence": 0.2, "method": "unclassified"}
