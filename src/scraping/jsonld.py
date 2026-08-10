from __future__ import annotations

import json
from datetime import date
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from src.models import JobRecord
from src.scraping.base import PoliteScraper


def _items(value: object) -> list[dict]:
    if isinstance(value, dict):
        if value.get("@type") == "JobPosting":
            return [value]
        if "@graph" in value:
            return [item for item in value["@graph"] if item.get("@type") == "JobPosting"]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict) and item.get("@type") == "JobPosting"]
    return []


class JsonLdJobScraper(PoliteScraper):
    """Generic adapter for permitted pages exposing schema.org JobPosting JSON-LD."""

    def __init__(self, url: str, **kwargs) -> None:
        parts = urlparse(url)
        super().__init__(f"{parts.scheme}://{parts.netloc}", **kwargs)

    def collect(self, url: str) -> list[JobRecord]:
        response = self.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        results: list[JobRecord] = []
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                payload = json.loads(script.string or "")
            except json.JSONDecodeError:
                continue
            for item in _items(payload):
                org = item.get("hiringOrganization") or {}
                address = (item.get("jobLocation") or {}).get("address") or {}
                base_salary = item.get("baseSalary") or {}
                value = base_salary.get("value") or {}
                results.append(
                    JobRecord(
                        source=urlparse(url).netloc,
                        source_url=item.get("url") or url,
                        title=item.get("title") or "Untitled",
                        company=org.get("name") or "Non précisé",
                        location=address.get("addressLocality") or address.get("addressRegion") or "Tunisie",
                        industry=item.get("industry") or "Autre",
                        description=BeautifulSoup(item.get("description") or "", "lxml").get_text(" ", strip=True),
                        posted_date=item.get("datePosted") or date.today().isoformat(),
                        contract_type=item.get("employmentType") or "Non précisé",
                        salary_min_tnd=value.get("minValue") or value.get("value"),
                        salary_max_tnd=value.get("maxValue") or value.get("value"),
                        salary_period=(value.get("unitText") or "").lower() or None,
                        scraped_at=self.now(),
                        raw_payload=item,
                    )
                )
        return results

