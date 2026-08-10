from src.nlp import detect_languages, extract_salary, extract_skills, infer_experience


def test_multilingual_extraction():
    text = "Junior Data Analyst: Python, SQL et Power BI. Français et English B2."
    skills = {item["skill"] for item in extract_skills(text)}
    assert {"python", "sql", "power_bi"}.issubset(skills)
    assert set(detect_languages(text)) == {"French", "English"}
    assert infer_experience(text) == "Entry-level"


def test_salary_range():
    assert extract_salary("Salaire 1800 - 2400 TND par mois") == (1800.0, 2400.0, "month")

