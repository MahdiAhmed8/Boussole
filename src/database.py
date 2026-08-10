from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd

from src.nlp import detect_languages, extract_skills, infer_experience
from src.settings import DB_PATH


def connect(path: str | Path = DB_PATH) -> duckdb.DuckDBPyConnection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))


def initialize(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id VARCHAR PRIMARY KEY, source VARCHAR, source_url VARCHAR, title VARCHAR,
            company VARCHAR, location VARCHAR, industry VARCHAR, description VARCHAR,
            posted_date DATE, contract_type VARCHAR, experience_level VARCHAR,
            language_requirements VARCHAR, salary_min_tnd DOUBLE, salary_max_tnd DOUBLE,
            salary_period VARCHAR, scraped_at TIMESTAMP, content_hash VARCHAR,
            is_demo BOOLEAN DEFAULT FALSE
        );
        CREATE TABLE IF NOT EXISTS job_skills (
            job_id VARCHAR, skill VARCHAR, display_skill VARCHAR, category VARCHAR,
            PRIMARY KEY (job_id, skill)
        );
        CREATE TABLE IF NOT EXISTS ingestion_runs (
            run_id VARCHAR, source VARCHAR, started_at TIMESTAMP, finished_at TIMESTAMP,
            status VARCHAR, rows_seen INTEGER, rows_loaded INTEGER, message VARCHAR
        );
    """)


def enrich_frame(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = frame.copy()
    frame["description"] = frame["description"].fillna("")
    frame["experience_level"] = frame.apply(
        lambda r: r.get("experience_level")
        if pd.notna(r.get("experience_level")) and str(r.get("experience_level")).strip()
        else infer_experience(f"{r.get('title', '')} {r.get('description', '')}"),
        axis=1,
    )
    frame["language_requirements"] = frame.apply(
        lambda r: json.dumps(detect_languages(f"{r.get('title', '')} {r.get('description', '')}")),
        axis=1,
    )
    frame["job_id"] = frame.apply(
        lambda r: duckdb.sql(
            "SELECT md5(?)", params=[f"{r.get('source','manual')}|{r.get('source_url','')}|{r.get('title','')}|{r.get('company','')}"]
        ).fetchone()[0],
        axis=1,
    )
    frame["content_hash"] = frame.apply(
        lambda r: duckdb.sql("SELECT md5(?)", params=[str(r.to_dict())]).fetchone()[0], axis=1
    )
    frame["scraped_at"] = pd.Timestamp.utcnow().tz_localize(None)
    frame["is_demo"] = frame.get("is_demo", False)

    skill_rows: list[dict[str, str]] = []
    for row in frame.itertuples():
        for skill in extract_skills(f"{row.title} {row.description}"):
            skill_rows.append({"job_id": row.job_id, **skill})
    return frame, pd.DataFrame(skill_rows, columns=["job_id", "skill", "display_skill", "category"])


def load_frame(con: duckdb.DuckDBPyConnection, frame: pd.DataFrame) -> int:
    jobs, skills = enrich_frame(frame)
    columns = [
        "job_id", "source", "source_url", "title", "company", "location", "industry",
        "description", "posted_date", "contract_type", "experience_level",
        "language_requirements", "salary_min_tnd", "salary_max_tnd", "salary_period",
        "scraped_at", "content_hash", "is_demo",
    ]
    for col in columns:
        if col not in jobs:
            jobs[col] = None
    jobs = jobs[columns]
    con.register("incoming_jobs", jobs)
    con.execute("DELETE FROM job_skills WHERE job_id IN (SELECT job_id FROM incoming_jobs)")
    con.execute("INSERT OR REPLACE INTO jobs SELECT * FROM incoming_jobs")
    if not skills.empty:
        con.register("incoming_skills", skills)
        con.execute("INSERT OR REPLACE INTO job_skills SELECT * FROM incoming_skills")
    return len(jobs)


def bootstrap_demo(con: duckdb.DuckDBPyConnection, path: str | Path) -> int:
    initialize(con)
    if con.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0:
        return load_frame(con, pd.read_csv(path))
    return 0
