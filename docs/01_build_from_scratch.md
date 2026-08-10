# Build the project from scratch

This chapter explains the reasoning behind the implementation, not just the commands.

## 1. Frame the research question

The unit of analysis is a **job listing at a point in time**. A listing can mention several skills, languages and locations. Keep the raw description because extraction rules will improve over time; derived fields can always be recomputed.

Define the questions before collecting data. This prevents collecting unnecessary personal data and makes the schema purposeful. For this project, we need the listing title, employer, location, industry, description, date, contract, seniority, salary when disclosed, source URL and retrieval time. We do not need applicant names, emails, CVs or account data.

## 2. Create the environment

Use Python 3.12 and isolate dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Why these packages:

- `httpx` handles web requests, timeouts and redirects.
- `BeautifulSoup` and `lxml` parse HTML.
- `DuckDB` gives analytical SQL without a server.
- `pandas` moves tabular data between ingestion, DuckDB and charts.
- `Plotly` creates interactive charts.
- `Streamlit` turns Python into a portfolio web app quickly.
- `pypdf` and `python-docx` read CVs locally.
- `scikit-learn` is available for a later TF-IDF extension.

## 3. Design the layers

Keep four layers separate:

1. **Collect**: source adapters return a common `JobRecord`.
2. **Normalize and enrich**: clean dates, infer seniority/languages, extract skills.
3. **Store and analyze**: DuckDB holds stable tables and executes analytics.
4. **Present**: Streamlit filters data; Plotly explains it.

This separation matters. A changed website should require editing one adapter, not the dashboard. A changed skill taxonomy should require re-enrichment, not recollection.

## 4. Initialize the database

```powershell
python cli.py init
```

The command creates the schema and loads the synthetic demonstration data only when the database is empty. The dashboard also bootstraps this on first run, which keeps onboarding simple.

## 5. Start the interface

```powershell
streamlit run app.py
```

Walk through each page and adjust the shared sidebar filters. The same filtered population is used for all metrics on a page, preventing mismatched denominators.

## 6. Replace demonstration data

Open **Data studio**, download the template and import permitted listings. Keep `is_demo=false`. You can delete the local DuckDB file and restart if you want a clean warehouse; the CSV seed remains in the repository so the portfolio never opens to an empty screen.

## 7. Validate

```powershell
pytest -q
ruff check .
```

Tests cover extraction, pair counts and idempotent loading. Add a fixture for every parsing edge case you discover. Scraper selector tests should use saved, permission-safe HTML fixtures instead of hitting live sites.

## 8. Extend it

Good next steps are a sanctioned ANETI feed, industry classification rules, Arabic normalization, location aliases, snapshot history for expired listings, and confidence scores for extracted requirements.

