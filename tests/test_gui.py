"""Unit tests for Module C GUI formatting and visualization helpers."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gui.gui import ArticlePresenter  # noqa: E402
from visualization.charts import (  # noqa: E402
    ArticleChartBuilder,
    count_by_category,
    count_by_publish_date,
    count_by_source,
)


SAMPLE_ARTICLES = [
    {
        "title": "AI investment rises",
        "source": "BBC News",
        "author": "Jane Doe",
        "publish_date": "2026-05-27T10:00:00Z",
        "url": "https://example.com/ai",
        "description": "A short summary.",
        "content": "Full article text.",
        "category": "technology",
    },
    {
        "title": "Market update",
        "source": {"name": "Reuters"},
        "author": None,
        "published_at": "2026-05-27",
        "url": "https://example.com/markets",
        "category": "business",
    },
    {
        "title": "Another AI story",
        "source": "BBC News",
        "publish_date": "2026-05-28",
        "category": "technology",
    },
]


class ArticlePresenterTests(unittest.TestCase):
    def test_labels_include_title_source_and_date(self) -> None:
        presenter = ArticlePresenter(SAMPLE_ARTICLES)

        labels = presenter.labels()

        self.assertEqual(len(labels), 3)
        self.assertIn("AI investment rises", labels[0])
        self.assertIn("BBC News", labels[0])
        self.assertIn("2026-05-27", labels[0])

    def test_detail_text_uses_fallbacks_for_missing_values(self) -> None:
        presenter = ArticlePresenter([{"title": "Untested URL"}])

        detail = presenter.detail_text(0)

        self.assertIn("Title: Untested URL", detail)
        self.assertIn("Source: Unknown source", detail)
        self.assertIn("Author: Unknown author", detail)
        self.assertIn("URL: No URL", detail)


class ChartSummaryTests(unittest.TestCase):
    def test_count_by_source_flattens_source_dictionary(self) -> None:
        counts = count_by_source(SAMPLE_ARTICLES)

        self.assertEqual(counts["BBC News"], 2)
        self.assertEqual(counts["Reuters"], 1)

    def test_count_by_category_groups_categories(self) -> None:
        counts = count_by_category(SAMPLE_ARTICLES)

        self.assertEqual(counts["technology"], 2)
        self.assertEqual(counts["business"], 1)

    def test_count_by_publish_date_normalises_iso_dates(self) -> None:
        counts = count_by_publish_date(SAMPLE_ARTICLES)

        self.assertEqual(counts["2026-05-27"], 2)
        self.assertEqual(counts["2026-05-28"], 1)

    def test_chart_builder_returns_matplotlib_figure(self) -> None:
        figure = ArticleChartBuilder().source_distribution(SAMPLE_ARTICLES)

        self.assertEqual(len(figure.axes), 1)
        self.assertEqual(figure.axes[0].get_title(), "Articles by Source")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
