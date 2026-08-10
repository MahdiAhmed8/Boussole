from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any


@dataclass
class JobRecord:
    source: str
    source_url: str
    title: str
    company: str = "Non précisé"
    location: str = "Tunisie"
    industry: str = "Autre"
    description: str = ""
    posted_date: date | str | None = None
    contract_type: str = "Non précisé"
    experience_level: str = "Non précisé"
    language_requirements: list[str] = field(default_factory=list)
    salary_min_tnd: float | None = None
    salary_max_tnd: float | None = None
    salary_period: str | None = None
    scraped_at: str | None = None
    raw_payload: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

