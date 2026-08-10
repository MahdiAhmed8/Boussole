from __future__ import annotations

import pandas as pd

REQUIRED = {"title", "company", "description", "posted_date"}
DEFAULTS = {
    "source": "manual",
    "source_url": "",
    "location": "Tunisie",
    "industry": "Autre",
    "contract_type": "Non précisé",
    "experience_level": "",
    "salary_min_tnd": None,
    "salary_max_tnd": None,
    "salary_period": "month",
    "is_demo": False,
}


def read_csv(path_or_buffer) -> pd.DataFrame:
    frame = pd.read_csv(path_or_buffer)
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    for column, default in DEFAULTS.items():
        if column not in frame:
            frame[column] = default
    frame["posted_date"] = pd.to_datetime(frame["posted_date"], errors="raise").dt.date
    return frame


def template() -> pd.DataFrame:
    return pd.DataFrame(
        [{
            "source": "manual", "source_url": "https://...", "title": "Data Analyst",
            "company": "Example", "location": "Tunis", "industry": "Technology",
            "description": "Python, SQL and Power BI. French required.",
            "posted_date": "2026-08-01", "contract_type": "CDI",
            "experience_level": "Entry-level", "salary_min_tnd": 1800,
            "salary_max_tnd": 2400, "salary_period": "month",
        }]
    )

