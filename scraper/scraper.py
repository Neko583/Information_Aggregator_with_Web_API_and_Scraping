"""News article scraper.

Author: Yuxiang Wang
Scope: BeautifulSoup-based extraction of article content, author, and publish
date from news article web pages, with graceful error handling.

The scraper is deliberately conservative: it never raises on a single bad page.
If a request fails or the HTML cannot be parsed, the returned dictionary still
includes the original URL plus an ``error`` field so the rest of the pipeline
can continue running.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Iterable, List, Optional

import requests
from bs4 import BeautifulSoup


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_TIMEOUT = 10  # seconds


@dataclass
class ScrapedArticle:
    """Container for the fields the scraper tries to recover from a page."""

    url: str
    title: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[str] = None
    content: Optional[str] = None
    source_domain: Optional[str] = None
    error: Optional[str] = None
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


class NewsScraper:
    """Fetches a news article page and extracts structured fields.

    The class wraps :mod:`requests` and :mod:`bs4` so the rest of the project
    only has to call :py:meth:`scrape_article` or :py:meth:`scrape_many`.
    """

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        timeout: int = DEFAULT_TIMEOUT,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout
        self.user_agent = user_agent

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def scrape_article(self, url: str) -> ScrapedArticle:
        """Scrape a single article URL.

        Always returns a :class:`ScrapedArticle`. On failure the ``error`` field
        is populated instead of raising.
        """

        if not url or not isinstance(url, str):
            return ScrapedArticle(url=str(url or ""), error="invalid url")

        try:
            response = self.session.get(
                url,
                headers={"User-Agent": self.user_agent},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            return ScrapedArticle(url=url, error=f"request failed: {exc}")

        try:
            soup = BeautifulSoup(response.text, "html.parser")
        except Exception as exc:  # pragma: no cover - bs4 rarely raises
            return ScrapedArticle(url=url, error=f"parse failed: {exc}")

        return ScrapedArticle(
            url=url,
            title=self._extract_title(soup),
            author=self._extract_author(soup),
            publish_date=self._extract_publish_date(soup),
            content=self._extract_content(soup),
            source_domain=self._extract_domain(url),
        )

    def scrape_many(self, urls: Iterable[str]) -> List[ScrapedArticle]:
        """Scrape an iterable of URLs and return the results in order."""

        return [self.scrape_article(url) for url in urls]

    # ------------------------------------------------------------------
    # Field extractors
    # ------------------------------------------------------------------
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        # Prefer OpenGraph title because it tends to be cleaner than <title>.
        og = soup.find("meta", attrs={"property": "og:title"})
        if og and og.get("content"):
            return og["content"].strip()

        if soup.title and soup.title.string:
            return soup.title.string.strip()

        h1 = soup.find("h1")
        if h1 and h1.get_text(strip=True):
            return h1.get_text(strip=True)

        return None

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        candidates = [
            ("meta", {"name": "author"}),
            ("meta", {"property": "article:author"}),
            ("meta", {"name": "byl"}),
        ]
        for tag, attrs in candidates:
            node = soup.find(tag, attrs=attrs)
            if node and node.get("content"):
                return node["content"].strip()

        byline = soup.find(attrs={"class": lambda c: bool(c) and "byline" in c.lower()})
        if byline:
            text = byline.get_text(" ", strip=True)
            if text:
                return text

        rel_author = soup.find("a", attrs={"rel": "author"})
        if rel_author and rel_author.get_text(strip=True):
            return rel_author.get_text(strip=True)

        return None

    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        candidates = [
            ("meta", {"property": "article:published_time"}),
            ("meta", {"name": "pubdate"}),
            ("meta", {"name": "publishdate"}),
            ("meta", {"name": "date"}),
        ]
        for tag, attrs in candidates:
            node = soup.find(tag, attrs=attrs)
            if node and node.get("content"):
                return node["content"].strip()

        time_tag = soup.find("time")
        if time_tag:
            if time_tag.get("datetime"):
                return time_tag["datetime"].strip()
            text = time_tag.get_text(strip=True)
            if text:
                return text

        return None

    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        # Try the semantic <article> element first; fall back to all <p> tags.
        article = soup.find("article")
        if article:
            paragraphs = [p.get_text(" ", strip=True) for p in article.find_all("p")]
            text = "\n".join(p for p in paragraphs if p)
            if text:
                return text

        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        text = "\n".join(p for p in paragraphs if p)
        return text or None

    def _extract_domain(self, url: str) -> Optional[str]:
        try:
            from urllib.parse import urlparse

            netloc = urlparse(url).netloc
            return netloc.lower() or None
        except Exception:
            return None
