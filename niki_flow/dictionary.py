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


def add_word(word):
    word = word.strip()
    if not word:
        return
    existing = {w.lower() for w in load_words()}
    if word.lower() in existing:
        return
    with open(DICTIONARY_PATH, "a", encoding="utf-8") as f:
        f.write(word + "\n")


def remove_word(word):
    if not DICTIONARY_PATH.exists():
        return
    target = word.strip().lower()
    lines = DICTIONARY_PATH.read_text(encoding="utf-8").splitlines()
    kept = [
        line
        for line in lines
        if line.strip().startswith("#")
        or not line.strip()
        or line.strip().lower() != target
    ]
    DICTIONARY_PATH.write_text("\n".join(kept) + "\n", encoding="utf-8")
