from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.database import connect, initialize, load_frame  # noqa: E402
from src.importers import read_csv  # noqa: E402
from src.scraping.jsonld import JsonLdJobScraper  # noqa: E402


def record_run(con, run_id: str, source: str, started, status: str, seen: int, loaded: int, message: str = ""):
    con.execute(
        "INSERT INTO ingestion_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [run_id, source, started, datetime.now(timezone.utc), status, seen, loaded, message[:1000]],
    )


def main() -> None:
    con = connect()
    initialize(con)
    inbox = ROOT / "data/raw/inbox"
    for csv_path in sorted(inbox.glob("*.csv")):
        run_id, started = str(uuid4()), datetime.now(timezone.utc)
        try:
            frame = read_csv(csv_path)
            count = load_frame(con, frame)
            record_run(con, run_id, f"csv:{csv_path.name}", started, "success", len(frame), count)
            print(json.dumps({"source": csv_path.name, "loaded": count}))
        except Exception as exc:
            record_run(con, run_id, f"csv:{csv_path.name}", started, "failed", 0, 0, str(exc))
            print(json.dumps({"source": csv_path.name, "error": str(exc)}))

    config = yaml.safe_load((ROOT / "config/sources.yml").read_text(encoding="utf-8"))
    for source in config.get("sources", []):
        if not source.get("enabled") or not source.get("permission_confirmed"):
            continue
        run_id, started = str(uuid4()), datetime.now(timezone.utc)
        try:
            records = []
            for url in source.get("urls", []):
                records.extend(JsonLdJobScraper(url).collect(url))
            frame = pd.DataFrame([record.to_dict() for record in records])
            count = load_frame(con, frame) if not frame.empty else 0
            record_run(con, run_id, source["name"], started, "success", len(records), count)
            print(json.dumps({"source": source["name"], "loaded": count}))
        except Exception as exc:
            record_run(con, run_id, source["name"], started, "failed", 0, 0, str(exc))
            print(json.dumps({"source": source["name"], "error": str(exc)}))


if __name__ == "__main__":
    main()

