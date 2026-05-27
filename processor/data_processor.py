"""News data processing utilities.

Author: Yuxiang Wang
Scope: clean raw article records, remove duplicates, and merge API responses
with the extra fields recovered by :class:`scraper.NewsScraper`.

Design notes
------------
* The processor is intentionally permissive about input shape. It accepts
  either plain ``dict`` records (as the News API tends to return) or any
  object that exposes attributes such as ``url``, ``title``, ``author``, etc.
  This keeps the module compatible with the ``Article`` class that another
  group member is responsible for.
* Output is always a plain ``dict`` so the GUI and integration code can pass
  it straight to widgets, ``json.dumps``, ``pandas``, etc.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, List, Optional


# Fields the processor normalises into the canonical article dictionary.
CANONICAL_FIELDS = (
    "url",
    "title",
    "author",
    "publish_date",
    "content",
    "description",
    "source",
    "category",
)


class DataProcessor:
    """Clean, deduplicate, and merge article records."""

    # ------------------------------------------------------------------
    # Cleaning
    # ------------------------------------------------------------------
    def clean_article(self, article: Any) -> dict:
        """Return a cleaned dictionary for a single article-like input.

        Whitespace is collapsed, empty strings become ``None``, and the
        ``source`` field is flattened if the API returned ``{"id": ..., "name": ...}``.
        """

        record = self._as_dict(article)
        cleaned: dict = {}

        for key in CANONICAL_FIELDS:
            value = record.get(key)
            if key == "source":
                cleaned[key] = self._clean_source(value)
            else:
                cleaned[key] = self._clean_text(value)

        # Preserve any other useful fields without modification.
        for key, value in record.items():
            if key not in cleaned:
                cleaned[key] = value

        return cleaned

    def clean_articles(self, articles: Iterable[Any]) -> List[dict]:
        return [self.clean_article(a) for a in articles if a is not None]

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------
    def remove_duplicates(self, articles: Iterable[Any]) -> List[dict]:
        """Drop duplicates, preferring the richer record when a clash occurs.

        Duplicates are detected first by URL, then by a normalised title.
        """

        seen_url: dict = {}
        seen_title: dict = {}
        result: List[dict] = []

        for article in articles:
            record = self.clean_article(article)
            url_key = (record.get("url") or "").strip().lower() or None
            title_key = self._normalise_title(record.get("title"))

            existing_index = None
            if url_key and url_key in seen_url:
                existing_index = seen_url[url_key]
            elif title_key and title_key in seen_title:
                existing_index = seen_title[title_key]

            if existing_index is None:
                result.append(record)
                index = len(result) - 1
                if url_key:
                    seen_url[url_key] = index
                if title_key:
                    seen_title[title_key] = index
            else:
                # Merge the duplicate into the existing record so we keep the
                # richest version (e.g. API record + scraped content).
                merged = self._prefer_richer(result[existing_index], record)
                result[existing_index] = merged
                if url_key:
                    seen_url[url_key] = existing_index
                if title_key:
                    seen_title[title_key] = existing_index

        return result

    # ------------------------------------------------------------------
    # Merging API + scraped data
    # ------------------------------------------------------------------
    def merge_with_scraped(
        self,
        api_articles: Iterable[Any],
        scraped_articles: Iterable[Any],
    ) -> List[dict]:
        """Combine API records with scraped detail records.

        Matching is by URL. Scraped fields fill in missing values and replace
        clearly weaker values (for example, an empty content string).
        """

        scraped_by_url: dict = {}
        for item in scraped_articles:
            record = self.clean_article(item)
            url = (record.get("url") or "").strip().lower()
            if url:
                scraped_by_url[url] = record

        merged: List[dict] = []
        for item in api_articles:
            api_record = self.clean_article(item)
            url = (api_record.get("url") or "").strip().lower()
            scraped_record = scraped_by_url.pop(url, None) if url else None

            if scraped_record:
                merged.append(self._prefer_richer(api_record, scraped_record))
            else:
                merged.append(api_record)

        # Any scraped records that did not match an API URL are still useful.
        for leftover in scraped_by_url.values():
            merged.append(leftover)

        return self.remove_duplicates(merged)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _as_dict(self, article: Any) -> dict:
        if isinstance(article, dict):
            return dict(article)
        if hasattr(article, "to_dict") and callable(article.to_dict):
            try:
                return dict(article.to_dict())
            except Exception:
                pass
        # Fall back to reading common attributes off the object.
        record: dict = {}
        for key in CANONICAL_FIELDS:
            if hasattr(article, key):
                record[key] = getattr(article, key)
        return record

    def _clean_text(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        collapsed = re.sub(r"\s+", " ", value).strip()
        return collapsed or None

    def _clean_source(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, dict):
            name = value.get("name") or value.get("id")
            return self._clean_text(name)
        return self._clean_text(value)

    def _normalise_title(self, title: Optional[str]) -> Optional[str]:
        if not title:
            return None
        text = re.sub(r"[^a-z0-9 ]+", " ", title.lower())
        text = re.sub(r"\s+", " ", text).strip()
        return text or None

    def _prefer_richer(self, base: dict, extra: dict) -> dict:
        """Return a merged dict where ``extra`` fills gaps in ``base``.

        For overlapping fields, the longer non-empty string wins. This keeps
        whichever copy carries more useful detail (typically the scraped one).
        """

        merged = dict(base)
        for key, value in extra.items():
            if value in (None, "", [], {}):
                continue
            current = merged.get(key)
            if current in (None, "", [], {}):
                merged[key] = value
                continue
            if isinstance(current, str) and isinstance(value, str):
                if len(value) > len(current):
                    merged[key] = value
        return merged
