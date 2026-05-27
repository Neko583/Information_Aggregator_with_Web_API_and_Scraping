"""Unit tests for the news scraper.

Author: Yuxiang Wang
The tests mock :class:`requests.Session` so no real HTTP traffic occurs.
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock

import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scraper.scraper import NewsScraper, ScrapedArticle  # noqa: E402


SAMPLE_HTML = """
<html>
  <head>
    <title>Fallback Title</title>
    <meta property="og:title" content="Real Headline" />
    <meta name="author" content="Jane Doe" />
    <meta property="article:published_time" content="2026-05-20T10:30:00Z" />
  </head>
  <body>
    <article>
      <p>First paragraph of the story.</p>
      <p>Second paragraph with more detail.</p>
    </article>
  </body>
</html>
"""


def _make_response(text: str = "", status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.text = text
    response.status_code = status_code
    response.raise_for_status = MagicMock()
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(f"status {status_code}")
    return response


class NewsScraperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = MagicMock(spec=requests.Session)
        self.scraper = NewsScraper(session=self.session)

    def test_scrape_article_returns_parsed_fields(self) -> None:
        self.session.get.return_value = _make_response(SAMPLE_HTML)

        article = self.scraper.scrape_article("https://example.com/news/story")

        self.assertIsInstance(article, ScrapedArticle)
        self.assertEqual(article.title, "Real Headline")
        self.assertEqual(article.author, "Jane Doe")
        self.assertEqual(article.publish_date, "2026-05-20T10:30:00Z")
        self.assertIn("First paragraph", article.content or "")
        self.assertIn("Second paragraph", article.content or "")
        self.assertEqual(article.source_domain, "example.com")
        self.assertIsNone(article.error)

    def test_scrape_article_falls_back_when_og_missing(self) -> None:
        html = "<html><head><title>Plain Title</title></head><body><p>Body text.</p></body></html>"
        self.session.get.return_value = _make_response(html)

        article = self.scraper.scrape_article("https://news.example/article")

        self.assertEqual(article.title, "Plain Title")
        self.assertIsNone(article.author)
        self.assertIn("Body text.", article.content or "")

    def test_scrape_article_handles_http_error(self) -> None:
        self.session.get.side_effect = requests.ConnectionError("no route")

        article = self.scraper.scrape_article("https://bad.example/")

        self.assertIsNotNone(article.error)
        self.assertIn("request failed", article.error or "")
        self.assertIsNone(article.title)

    def test_scrape_article_handles_bad_status(self) -> None:
        self.session.get.return_value = _make_response("", status_code=500)

        article = self.scraper.scrape_article("https://bad.example/page")

        self.assertIsNotNone(article.error)
        self.assertIn("status 500", article.error or "")

    def test_scrape_article_rejects_invalid_url(self) -> None:
        article = self.scraper.scrape_article("")
        self.assertEqual(article.error, "invalid url")
        self.session.get.assert_not_called()

    def test_scrape_many_preserves_order(self) -> None:
        responses = [
            _make_response("<html><title>One</title></html>"),
            _make_response("<html><title>Two</title></html>"),
        ]
        self.session.get.side_effect = responses

        results = self.scraper.scrape_many(
            ["https://a.example/1", "https://b.example/2"]
        )

        self.assertEqual([r.title for r in results], ["One", "Two"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
