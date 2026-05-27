"""Unit tests for the data processor.

Author: Yuxiang Wang
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from processor.data_processor import DataProcessor  # noqa: E402


class DataProcessorCleaningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.processor = DataProcessor()

    def test_clean_article_normalises_whitespace(self) -> None:
        raw = {
            "title": "  Multi   space   Title  ",
            "content": "Line one.\n\nLine two.",
            "url": "https://example.com/story",
            "author": "  Jane Doe  ",
        }
        cleaned = self.processor.clean_article(raw)

        self.assertEqual(cleaned["title"], "Multi space Title")
        self.assertEqual(cleaned["author"], "Jane Doe")
        self.assertEqual(cleaned["content"], "Line one. Line two.")
        self.assertEqual(cleaned["url"], "https://example.com/story")

    def test_clean_article_flattens_source_dict(self) -> None:
        cleaned = self.processor.clean_article(
            {"title": "X", "source": {"id": "bbc-news", "name": "BBC News"}}
        )
        self.assertEqual(cleaned["source"], "BBC News")

    def test_clean_article_empty_string_becomes_none(self) -> None:
        cleaned = self.processor.clean_article({"title": "   ", "url": ""})
        self.assertIsNone(cleaned["title"])
        self.assertIsNone(cleaned["url"])

    def test_clean_article_accepts_object_with_attributes(self) -> None:
        class Stub:
            url = "https://example.com/x"
            title = "Story"
            author = "Author"
            publish_date = "2026-01-01"
            content = "Body"
            description = None
            source = None
            category = None

        cleaned = self.processor.clean_article(Stub())
        self.assertEqual(cleaned["title"], "Story")
        self.assertEqual(cleaned["url"], "https://example.com/x")


class DataProcessorDedupeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.processor = DataProcessor()

    def test_remove_duplicates_by_url(self) -> None:
        articles = [
            {"url": "https://a.com/1", "title": "A"},
            {"url": "https://a.com/1", "title": "A duplicate"},
            {"url": "https://b.com/2", "title": "B"},
        ]
        result = self.processor.remove_duplicates(articles)
        self.assertEqual(len(result), 2)
        urls = {r["url"] for r in result}
        self.assertEqual(urls, {"https://a.com/1", "https://b.com/2"})

    def test_remove_duplicates_by_title_when_url_missing(self) -> None:
        articles = [
            {"title": "Breaking news!"},
            {"title": "breaking news"},
            {"title": "Other story"},
        ]
        result = self.processor.remove_duplicates(articles)
        self.assertEqual(len(result), 2)

    def test_remove_duplicates_keeps_richer_record(self) -> None:
        articles = [
            {"url": "https://a.com/1", "title": "A", "content": "short"},
            {"url": "https://a.com/1", "title": "A", "content": "a much longer body of the article"},
        ]
        result = self.processor.remove_duplicates(articles)
        self.assertEqual(len(result), 1)
        self.assertIn("longer body", result[0]["content"])


class DataProcessorMergeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.processor = DataProcessor()

    def test_merge_fills_in_missing_fields_from_scraped(self) -> None:
        api = [
            {
                "url": "https://a.com/1",
                "title": "Headline",
                "author": None,
                "content": None,
                "source": {"name": "Example"},
            }
        ]
        scraped = [
            {
                "url": "https://a.com/1",
                "author": "Jane Doe",
                "content": "Full article body recovered by scraping.",
                "publish_date": "2026-05-20T10:30:00Z",
            }
        ]
        merged = self.processor.merge_with_scraped(api, scraped)

        self.assertEqual(len(merged), 1)
        record = merged[0]
        self.assertEqual(record["title"], "Headline")
        self.assertEqual(record["author"], "Jane Doe")
        self.assertEqual(record["source"], "Example")
        self.assertIn("Full article body", record["content"])
        self.assertEqual(record["publish_date"], "2026-05-20T10:30:00Z")

    def test_merge_keeps_unmatched_scraped_records(self) -> None:
        api = [{"url": "https://a.com/1", "title": "A"}]
        scraped = [{"url": "https://b.com/2", "title": "Extra", "content": "Body"}]
        merged = self.processor.merge_with_scraped(api, scraped)

        urls = {r["url"] for r in merged}
        self.assertEqual(urls, {"https://a.com/1", "https://b.com/2"})

    def test_merge_deduplicates_result(self) -> None:
        api = [
            {"url": "https://a.com/1", "title": "A"},
            {"url": "https://a.com/1", "title": "A"},
        ]
        scraped = []
        merged = self.processor.merge_with_scraped(api, scraped)
        self.assertEqual(len(merged), 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
