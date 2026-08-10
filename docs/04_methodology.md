# NLP and analytical methodology

## Why start with a dictionary matcher

Job-market dashboards must be auditable. A curated taxonomy makes every match explainable: `powerbi` and `power bi` map to `power_bi`. Word boundaries reduce false matches such as `R` appearing inside ordinary words. The taxonomy lives in `config/skills.yml`, so a reviewer can inspect and edit it without retraining a model.

The tradeoff is recall. Novel spellings and implied skills are missed. Measure precision and recall on a hand-labelled sample before presenting results as research.

## Multilingual handling

The pipeline searches French, English and Arabic signals. Language charts count **explicit requirements**. They do not infer the language of the full advert, and one listing can require multiple languages. Keep this distinction in captions.

Seniority uses high-precision phrases such as “junior,” “stage,” “3 ans” and “senior.” Conflicts should be resolved with a priority rule or marked for review. A production model could add spaCy `PhraseMatcher` patterns and a labelled classifier.

## Skill frequency

The denominator is unique filtered listings. A skill counts at most once per listing:

`skill share = listings mentioning skill / all filtered listings`

Raw mention counts are not used because repeating “Python” three times in one advert should not triple demand.

## Co-occurrence

For each listing, generate every unordered pair of unique extracted skills. Count each pair once. High counts reveal bundles but not causality. A common skill naturally pairs often; add lift later:

`lift(A,B) = P(A and B) / (P(A) × P(B))`

Use a minimum support threshold on real datasets to avoid highlighting one-off combinations.

## Monthly changes

Monthly charts group by `posted_date`. When coverage by source changes, the line may reflect collection changes rather than employer demand. Maintain a source-by-month coverage table and compare like-for-like sources. Partial current months should be visually marked or excluded from growth claims.

## Salary analysis

Only disclosed ranges enter pay charts. The midpoint is `(minimum + maximum) / 2`; this is a descriptive convenience, not an offered salary. Always show coverage. Normalize annual/hourly values and document gross versus net assumptions before combining them.

## CV matching

The CV is parsed in memory and is not written to DuckDB. Extracted CV skills are compared with each job’s canonical skill set:

`match score = matched required skills / extracted required skills`

This is a transparent skill-overlap score, not a hiring probability. TF-IDF cosine similarity over the CV and job text is used only to order roles with the same skill-coverage score; it does not change the displayed score. The approach ignores years of experience, education, soft-skill evidence and skill proficiency. Never use it to screen people automatically.

## Validation plan

Randomly label at least 200 diverse listings. For each skill/language/seniority field, compute precision, recall and F1. Report macro and per-class results. Review errors by language and industry. Version the taxonomy and rerun historical enrichment so trend changes do not come from inconsistent extraction logic.
