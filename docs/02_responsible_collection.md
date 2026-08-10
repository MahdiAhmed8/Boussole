# Responsible collection playbook

This is an engineering control document, not legal advice. Educational purpose does not by itself override terms, copyright, database rights, privacy rules or access controls.

## Source approval checklist

Before adding a source, record:

- source owner and contact;
- exact pages or API/feed endpoints in scope;
- permission basis: open licence, written permission, API terms, public-sector release or manual export;
- terms-of-use URL and review date;
- `robots.txt` result and review date;
- fields collected and why each is necessary;
- request rate, run frequency and retention period;
- how removals/corrections will be handled.

Do not collect from logged-in pages, bypass CAPTCHAs or rate limits, rotate identities, or extract candidate data. Do not republish full descriptions unless the licence permits it. For a public dashboard, consider publishing aggregates and source links rather than copied text.

## Project safeguards

The generic collector:

- has a named user agent you should replace with your real contact email;
- checks `robots.txt` before a page request;
- refuses collection when rules cannot be retrieved or do not permit it;
- enforces a minimum one-second delay;
- prevents requests from leaving the configured host;
- extracts standardized `JobPosting` JSON-LD rather than fragile visual markup;
- stores provenance and retrieval time;
- is disabled in `config/sources.yml` until permission is confirmed.

These are minimum safeguards, not proof of permission.

## Source notes checked for this project

- [Tunisie Travail terms](https://www.tunisietravail.net/cgu/) explicitly prohibit automated robots/scrapers. Do not automate that site.
- [Keejob terms](https://www.keejob.com/terms-of-use/) say offers remain the property of their authors. Seek written authorization or an approved feed for bulk reuse.
- [ANETI](https://www.emploi.nat.tn/fo/Fr2026/global.php?menu1=143) is the public employment agency and publishes access-to-information contacts and forms. Requesting a reusable dataset/feed is preferable to reverse-engineering pages.

Re-check these pages before every new source release because policies change.

## Manual collection protocol

Manual collection still needs provenance. Save one row per listing with its canonical URL and date. Record only employer-posted information needed for aggregate research. Review a small random sample after entry. Use a second reviewer if the results will support claims beyond a portfolio demonstration.

## Removal and correction

Keep `source_url` as the trace key. If an owner requests removal, identify affected records, remove them from the warehouse and generated exports, rerun derived statistics, and record the action. Avoid immutable public snapshots containing copied descriptions.

