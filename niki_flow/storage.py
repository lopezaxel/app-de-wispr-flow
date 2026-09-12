import difflib
import sqlite3
from datetime import datetime, timezone

from .config import HISTORY_DB_PATH


def _connect():
    HISTORY_DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(HISTORY_DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dictations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                final_text TEXT NOT NULL,
                was_edited INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dictation_id INTEGER NOT NULL,
                original_phrase TEXT NOT NULL,
                corrected_phrase TEXT NOT NULL,
                FOREIGN KEY (dictation_id) REFERENCES dictations(id)
            )
            """
        )


def _extract_corrections(raw_text, final_text):
    raw_words = raw_text.split()
    final_words = final_text.split()
    matcher = difflib.SequenceMatcher(None, raw_words, final_words)
    corrections = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace":
            corrections.append(
                (" ".join(raw_words[i1:i2]), " ".join(final_words[j1:j2]))
            )
    return corrections


def log_dictation(raw_text, final_text):
    was_edited = raw_text.strip() != final_text.strip()
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO dictations (created_at, raw_text, final_text, was_edited) "
            "VALUES (?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), raw_text, final_text, int(was_edited)),
        )
        dictation_id = cur.lastrowid
        if was_edited:
            for original, corrected in _extract_corrections(raw_text, final_text):
                conn.execute(
                    "INSERT INTO corrections (dictation_id, original_phrase, corrected_phrase) "
                    "VALUES (?, ?, ?)",
                    (dictation_id, original, corrected),
                )
    return dictation_id


def get_stats():
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM dictations").fetchone()[0]
        edited = conn.execute(
            "SELECT COUNT(*) FROM dictations WHERE was_edited = 1"
        ).fetchone()[0]
        rows = conn.execute("SELECT final_text FROM dictations").fetchall()
        total_words = sum(len(text.split()) for (text,) in rows)
        return {
            "total_dictations": total,
            "edited_dictations": edited,
            "total_words": total_words,
        }


def get_history(limit=200):
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, created_at, raw_text, final_text, was_edited "
            "FROM dictations ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        keys = ("id", "created_at", "raw_text", "final_text", "was_edited")
        return [dict(zip(keys, row)) for row in rows]


def get_correction_summary():
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT original_phrase, corrected_phrase, COUNT(*) as count
            FROM corrections
            GROUP BY original_phrase, corrected_phrase
            ORDER BY count DESC, corrected_phrase
            """
        ).fetchall()
        keys = ("original_phrase", "corrected_phrase", "count")
        return [dict(zip(keys, row)) for row in rows]
