from .config import DICTIONARY_PATH


def load_words():
    if not DICTIONARY_PATH.exists():
        return []
    with open(DICTIONARY_PATH, "r", encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]


def build_prompt():
    words = load_words()
    if not words:
        return ""
    return "Vocabulario y nombres propios frecuentes: " + ", ".join(words) + "."
