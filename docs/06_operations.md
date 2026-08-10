# Operations and periodic updates

## Local refresh

Put authorized CSV files in `data/raw/inbox/`, or configure approved JSON-LD URLs. Then run:

```powershell
python scripts/update_data.py
pytest -q
streamlit run app.py
```

The batch script logs every source attempt in `ingestion_runs`. It does not move or delete inbox files; idempotent IDs make repeat runs safe.

## Configure an automated source

Edit `config/sources.yml`:

```yaml
sources:
  - name: approved_employer_feed
    type: jsonld_urls
    enabled: true
    permission_confirmed: true
    urls:
      - https://careers.example.tn/jobs/data-analyst
```

Only set `permission_confirmed` after recording the approval checklist. Replace the user-agent email in `.env`. Test one URL locally. Keep the page limit and delay conservative.

## Scheduling

The included GitHub Actions workflow runs every Monday at 05:20 UTC and on demand. It runs the updater and tests, but intentionally does not commit the DuckDB file. Choose one deployment pattern:

- upload the database as a versioned workflow artifact for manual review;
- upload aggregate Parquet/CSV to permitted object storage;
- deploy to a managed database used by the dashboard;
- open an automated pull request containing reviewed aggregate data only.

Do not commit copied descriptions into a public repository unless reuse rights clearly permit it.

## Monitoring checklist

After each run, inspect:

- run status and rows loaded by source;
- unexpected zero-row sources;
- duplicate URL rate;
- missing description/location/industry rates;
- skill extraction rate;
- salary and language coverage;
- maximum and minimum posted dates;
- source share changes that could distort trends.

Set alerts only after observing normal variability. A zero-row run may mean “no new jobs,” a changed page, or revoked access; investigate without bypassing controls.

## Reproducible releases

Tag each public dashboard release with collection window, source list, taxonomy version, code commit and row count. Export aggregates with a README describing denominators and exclusions. Archive approval records separately from public data.

## Recovery

DuckDB is a single file. Stop the app before copying it, then keep dated backups outside the repository. To rebuild, create a fresh database and replay approved source exports through the importer. This is safer than treating a binary database as the only copy of research evidence.

