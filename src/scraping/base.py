from __future__ import annotations

import time
import urllib.robotparser
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import httpx

from src.models import JobRecord
from src.settings import REQUEST_DELAY_SECONDS, USER_AGENT


class CollectionNotPermitted(RuntimeError):
    """Raised when robots.txt does not permit collection for our user agent."""


class PoliteScraper(ABC):
    def __init__(self, base_url: str, delay: float = REQUEST_DELAY_SECONDS) -> None:
        self.base_url = base_url.rstrip("/")
        self.delay = max(delay, 1.0)
        self.client = httpx.Client(
            headers={"User-Agent": USER_AGENT, "Accept-Language": "fr,en;q=0.8"},
            timeout=25,
            follow_redirects=True,
        )
        self._last_request = 0.0

    def _allowed(self, url: str) -> bool:
        robots_url = urljoin(self.base_url + "/", "robots.txt")
        parser = urllib.robotparser.RobotFileParser(robots_url)
        try:
            response = self.client.get(robots_url)
            if response.status_code >= 400:
                return False  # fail closed: obtain permission or use manual import
            parser.parse(response.text.splitlines())
            return parser.can_fetch(USER_AGENT, url)
        except httpx.HTTPError:
            return False

    def get(self, url: str) -> httpx.Response:
        if urlparse(url).netloc != urlparse(self.base_url).netloc:
            raise ValueError("Scraper may only request its configured host")
        if not self._allowed(url):
            raise CollectionNotPermitted(
                f"robots.txt did not explicitly permit access to {url}. Use CSV import or obtain permission."
            )
        wait = self.delay - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        response = self.client.get(url)
        self._last_request = time.monotonic()
        response.raise_for_status()
        return response

    @abstractmethod
    def collect(self, url: str) -> list[JobRecord]: ...

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

