import pandas as pd

from src.analytics import skill_cooccurrence


def test_cooccurrence_counts_once_per_job():
    rows = pd.DataFrame([
        {"job_id": "1", "display_skill": "Python"},
        {"job_id": "1", "display_skill": "SQL"},
        {"job_id": "2", "display_skill": "Python"},
        {"job_id": "2", "display_skill": "SQL"},
    ])
    result = skill_cooccurrence(rows)
    assert result.iloc[0].to_dict() == {"skill_a": "Python", "skill_b": "SQL", "jobs": 2}

