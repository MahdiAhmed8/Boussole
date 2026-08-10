import duckdb
import pandas as pd

from src.database import initialize, load_frame


def test_load_is_idempotent():
    con = duckdb.connect(":memory:")
    initialize(con)
    frame = pd.DataFrame([{
        "source": "manual", "source_url": "https://example.com/1", "title": "Data Analyst",
        "company": "Acme", "location": "Tunis", "industry": "Tech",
        "description": "Python SQL", "posted_date": "2026-01-01", "contract_type": "CDI",
        "experience_level": "Entry-level", "salary_min_tnd": 1000,
        "salary_max_tnd": 1500, "salary_period": "month", "is_demo": False,
    }])
    load_frame(con, frame)
    load_frame(con, frame)
    assert con.execute("select count(*) from jobs").fetchone()[0] == 1
    assert con.execute("select count(*) from job_skills").fetchone()[0] == 2

