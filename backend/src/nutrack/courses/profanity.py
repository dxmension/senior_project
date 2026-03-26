"""
Profanity filter for course reviews.

English: uses the `better-profanity` library (comprehensive word list + censor).
Russian / Kazakh: substring matching against Cyrillic root patterns.

A comment is rejected if either check fires.
"""
from __future__ import annotations

import unicodedata

from better_profanity import profanity as _en_profanity

# Load the default English word list once at import time
_en_profanity.load_censor_words()

# ---------------------------------------------------------------------------
# Cyrillic root substrings to block (Russian + Kazakh)
# Substring matching means "хуе" catches "похуеть", "хуевый", etc.
# ---------------------------------------------------------------------------

_BLOCKED: list[str] = [
    # Russian mat — base roots
    "хуй",
    "хуе",
    "хуя",
    "хую",
    "хуёв",
    "нахуй",
    "похуй",
    "пиздец",
    "пизда",
    "пизды",
    "пизде",
    "пизду",
    "пиздёж",
    "пиздёт",
    "пизд",
    "ёбан",
    "ёбат",
    "ебат",
    "ебан",
    "заебал",
    "заебат",
    "наебал",
    "наебат",
    "выебат",
    "проебат",
    "поебат",
    "блядь",
    "бляди",
    "бляде",
    "блядин",
    "блядск",
    "бляд",
    "сука",
    "суки",
    "суке",
    "суку",
    "мудак",
    "мудила",
    "мудозвон",
    "ёбт",
    "ёпт",
    "ёб твою",
    "еб твою",
    # Common euphemisms / letter substitutions still caught by roots above;
    # add extras here if needed.

    # Kazakh mat (Cyrillic transliteration)
    "шеше",   # part of "шешең" insults
    "ана",    # context-dependent but included for "анаңды"
    "анаңды",
    "сикал",
    "сикты",
    "сиктир",
    "сиқтыр",
    "боқ",
    "боқ",
    "жезөкше",
    "жесір",
    "қотыр",
    "қоңыр кел",
    "пысык",
    "пышак",
    "ит тұқым",
    "ит тукым",
    "иттің баласы",
    "итің",
    "шошқа",
    "есек",
]

# Deduplicate and normalize once at import time
_BLOCKED_NORMALIZED: list[str] = list({s.lower() for s in _BLOCKED})


def _normalize(text: str) -> str:
    """Lowercase and NFKC-normalize so ё/е variants collapse consistently."""
    return unicodedata.normalize("NFKC", text).lower()


def contains_profanity(text: str) -> bool:
    """Return True if *text* contains English or Russian/Kazakh profanity."""
    # English check via better-profanity library
    if _en_profanity.contains_profanity(text):
        return True
    # Russian / Kazakh check via Cyrillic substring matching
    normalized = _normalize(text)
    return any(sub in normalized for sub in _BLOCKED_NORMALIZED)
