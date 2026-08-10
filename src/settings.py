from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("TJMI_DB_PATH", ROOT / "data/warehouse/jobs.duckdb"))
SKILLS_PATH = ROOT / "config/skills.yml"
DEMO_DATA_PATH = ROOT / "data/sample_jobs.csv"
USER_AGENT = os.getenv(
    "TJMI_USER_AGENT", "TunisiaJobMarketResearch/1.0 (+research@example.com)"
)
REQUEST_DELAY_SECONDS = float(os.getenv("TJMI_REQUEST_DELAY_SECONDS", "2.0"))
MAX_PAGES = int(os.getenv("TJMI_MAX_PAGES", "5"))

