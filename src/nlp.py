from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

from src.settings import SKILLS_PATH


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


@lru_cache(maxsize=4)
def load_taxonomy(path: str | Path = SKILLS_PATH) -> dict[str, dict[str, list[str]]]:
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)["categories"]


def extract_skills(text: str) -> list[dict[str, str]]:
    """Dictionary matcher with careful token boundaries; deterministic and auditable."""
    normalized = _normalize(text)
    matches: list[dict[str, str]] = []
    for category, skills in load_taxonomy().items():
        for canonical, aliases in skills.items():
            for alias in aliases:
                pattern = rf"(?<![\w]){re.escape(alias.lower())}(?![\w])"
                if re.search(pattern, normalized):
                    matches.append(
                        {"skill": canonical, "display_skill": canonical.replace("_", " ").title(), "category": category}
                    )
                    break
    return matches


def detect_languages(text: str) -> list[str]:
    text = _normalize(text)
    patterns = {
        "French": [r"\bfran[cç]ais\b", r"\bfrench\b", r"\bfrancophone\b"],
        "English": [r"\banglais\b", r"\benglish\b", r"\banglophone\b"],
        "Arabic": [r"\barabe\b", r"\barabic\b", r"[\u0600-\u06ff]"],
    }
    return [language for language, pats in patterns.items() if any(re.search(p, text) for p in pats)]


def infer_experience(text: str) -> str:
    text = _normalize(text)
    if re.search(r"\b(stage|stagiaire|internship|intern)\b", text):
        return "Internship"
    if re.search(r"\b(junior|débutant|debutant|fresh graduate|entry.level|0\s*[-–]\s*2 ans)\b", text):
        return "Entry-level"
    if re.search(r"\b(senior|lead|expert|manager|5\+? ans|plus de 5 ans)\b", text):
        return "Senior"
    if re.search(r"\b(2\s*[-–]\s*5 ans|3 ans|4 ans|confirmé|confirme)\b", text):
        return "Mid-level"
    return "Non précisé"


def extract_salary(text: str) -> tuple[float | None, float | None, str | None]:
    text = _normalize(text).replace(" ", "")
    match = re.search(r"(\d{3,5})(?:[-–à](\d{3,5}))?(?:tnd|dt|dinar)", text)
    if not match:
        return None, None, None
    low = float(match.group(1))
    high = float(match.group(2) or match.group(1))
    period = "year" if re.search(r"an|année|annuel", text) else "month"
    return low, high, period

