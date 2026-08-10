from __future__ import annotations

from itertools import combinations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def skill_cooccurrence(skill_rows: pd.DataFrame, minimum: int = 1) -> pd.DataFrame:
    pairs: dict[tuple[str, str], int] = {}
    for _, group in skill_rows.groupby("job_id"):
        skills = sorted(set(group["display_skill"]))
        for left, right in combinations(skills, 2):
            pairs[(left, right)] = pairs.get((left, right), 0) + 1
    rows = [
        {"skill_a": pair[0], "skill_b": pair[1], "jobs": count}
        for pair, count in pairs.items() if count >= minimum
    ]
    return pd.DataFrame(rows).sort_values("jobs", ascending=False) if rows else pd.DataFrame(
        columns=["skill_a", "skill_b", "jobs"]
    )


def cv_match(cv_text: str, jobs: pd.DataFrame, job_skills: pd.DataFrame, extractor) -> pd.DataFrame:
    cv_skills = {item["skill"] for item in extractor(cv_text)}
    documents = [cv_text] + (jobs["title"].fillna("") + " " + jobs["description"].fillna("")).tolist()
    vectors = TfidfVectorizer(ngram_range=(1, 2), min_df=1).fit_transform(documents)
    similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
    rows = []
    for index, job in enumerate(jobs.itertuples()):
        required = set(job_skills.loc[job_skills.job_id == job.job_id, "skill"])
        matched = cv_skills & required
        missing = required - cv_skills
        score = round(100 * len(matched) / len(required)) if required else 0
        rows.append({
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "match_score": score,
            "text_similarity": round(float(similarities[index]) * 100, 1),
            "matched": ", ".join(sorted(s.replace("_", " ").title() for s in matched)) or "—",
            "missing": ", ".join(sorted(s.replace("_", " ").title() for s in missing)) or "—",
            "source_url": job.source_url,
        })
    return pd.DataFrame(rows).sort_values(
        ["match_score", "text_similarity", "title"], ascending=[False, False, True]
    )
