# Boussole — Tunisia Job-Market Intelligence

A portfolio-ready Streamlit platform for measuring which skills Tunisian employers request. It combines a reproducible collection layer, multilingual NLP, DuckDB analytics, Plotly storytelling and local CV-to-job matching.

> The repository starts with a **synthetic demo dataset** so every dashboard works immediately. Demo rows are never presented as observed market facts. Replace or supplement them with public, manually collected, licensed or otherwise permitted data in **Data studio**.

## What the platform answers

- Where are listings concentrated by governorate/city and industry?
- Which technologies and professional skills appear most often?
- Which skills co-occur (for example Python + SQL + Power BI)?
- How do entry-level, mid-level and senior roles differ?
- How often do employers explicitly request French, English or Arabic?
- What do disclosed salary ranges suggest, and how complete is the evidence?
- Which skills are gaining or losing monthly demand?
- Which roles best match a CV, and what is missing?

## Run it locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python cli.py init
streamlit run app.py
```

Open the local address Streamlit prints (usually `http://localhost:8501`). The app creates `data/warehouse/jobs.duckdb` automatically.

## Update the data

The safest default is manual/licensed import:

1. Open **Data studio → Import CSV**.
2. Download the template.
3. Add listings you are allowed to analyze; never include candidate personal data.
4. Confirm permission and import.

For permitted pages that publish schema.org `JobPosting` JSON-LD, add URLs to `config/sources.yml`, confirm both flags, and run:

```powershell
python scripts/update_data.py
```

The collector identifies itself, checks `robots.txt`, waits between requests, stays on the configured host, and fails closed. A weekly GitHub Actions skeleton is included; it remains inert for web sources until you explicitly approve and enable one.

## Project map

```text
app.py                     Streamlit experience
cli.py                     Initialization and one-off imports
config/skills.yml          Auditable multilingual skill taxonomy
config/sources.yml         Disabled-by-default source registry
src/database.py            DuckDB schema, enrichment, deduplication
src/nlp.py                 Skills, languages, seniority, salary parsing
src/analytics.py           Co-occurrence and CV matching
src/scraping/              Polite generic JSON-LD collection adapter
scripts/update_data.py     Repeatable batch refresh pipeline
data/sample_jobs.csv       Synthetic portfolio demonstration data
docs/                      Rebuild and methodology handbook
tests/                     Unit tests for core logic
```

## Responsible-use boundary

Publicly visible does not automatically mean reusable. Check a source’s terms, robots.txt, copyright/database rights, and privacy obligations. Prefer official APIs, feeds, employer career pages with permission, open data, or manual exports. For example, Tunisie Travail’s current terms explicitly prohibit automated scraping; this project therefore does not ship an adapter for it. Keejob states that listing content remains owned by its authors, so obtain permission before bulk collection. ANETI publishes job information and an access-to-information channel, which is a good place to request a sanctioned feed or dataset.

See [Responsible collection](docs/02_responsible_collection.md) before enabling any source.

## Documentation

- [Build from scratch](docs/01_build_from_scratch.md)
- [Responsible collection](docs/02_responsible_collection.md)
- [Data model and pipeline](docs/03_data_model.md)
- [NLP and analytical methodology](docs/04_methodology.md)
- [Dashboard design and portfolio story](docs/05_dashboard_and_portfolio.md)
- [Operations and periodic updates](docs/06_operations.md)

