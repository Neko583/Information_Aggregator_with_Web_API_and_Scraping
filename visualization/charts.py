"""Matplotlib chart helpers for Module C.

The GUI imports this module to build visual summaries of the aggregated
articles.  The functions return Matplotlib ``Figure`` objects instead of
calling ``plt.show()``, so they can be embedded in Tkinter or tested without
opening a window.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any, Iterable, Optional

from matplotlib.figure import Figure


UNKNOWN_SOURCE = "Unknown source"
UNKNOWN_CATEGORY = "Uncategorised"


def article_to_dict(article: Any) -> dict:
    """Convert a dict, dataclass-like object, or Article instance to a dict."""

    if isinstance(article, dict):
        record = dict(article)
    elif hasattr(article, "to_dict") and callable(article.to_dict):
        record = dict(article.to_dict())
    else:
        record = {}
        for key in (
            "title",
            "source",
            "author",
            "published_at",
            "publish_date",
            "url",
            "description",
            "content",
            "category",
        ):
            if hasattr(article, key):
                record[key] = getattr(article, key)

    if isinstance(record.get("source"), dict):
        source = record["source"].get("name") or record["source"].get("id")
        record["source"] = source

    if "publish_date" not in record and "published_at" in record:
        record["publish_date"] = record.get("published_at")

    return record


def count_by_source(articles: Iterable[Any]) -> Counter:
    """Return article counts grouped by source name."""

    counts: Counter = Counter()
    for article in articles:
        record = article_to_dict(article)
        source = _clean_label(record.get("source"), UNKNOWN_SOURCE)
        counts[source] += 1
    return counts


def count_by_category(articles: Iterable[Any]) -> Counter:
    """Return article counts grouped by category."""

    counts: Counter = Counter()
    for article in articles:
        record = article_to_dict(article)
        category = _clean_label(record.get("category"), UNKNOWN_CATEGORY)
        counts[category] += 1
    return counts


def count_by_publish_date(articles: Iterable[Any]) -> Counter:
    """Return article counts grouped by YYYY-MM-DD publish date."""

    counts: Counter = Counter()
    for article in articles:
        record = article_to_dict(article)
        date_label = _normalise_date(record.get("publish_date"))
        if date_label:
            counts[date_label] += 1
    return counts


class ArticleChartBuilder:
    """Build Matplotlib figures for aggregated news data."""

    def __init__(self, figsize: tuple[float, float] = (6.4, 4.2)) -> None:
        self.figsize = figsize

    def source_distribution(self, articles: Iterable[Any]) -> Figure:
        """Create a bar chart showing article counts by source."""

        return self._bar_chart(
            count_by_source(articles),
            title="Articles by Source",
            xlabel="Source",
            ylabel="Articles",
        )

    def category_distribution(self, articles: Iterable[Any]) -> Figure:
        """Create a bar chart showing article counts by category."""

        return self._bar_chart(
            count_by_category(articles),
            title="Articles by Category",
            xlabel="Category",
            ylabel="Articles",
        )

    def publication_timeline(self, articles: Iterable[Any]) -> Figure:
        """Create a line chart showing article counts by publish date."""

        counts = count_by_publish_date(articles)
        figure = Figure(figsize=self.figsize, dpi=100)
        axis = figure.add_subplot(111)

        if not counts:
            self._empty_chart(axis, "No publication dates available")
            return figure

        labels = sorted(counts)
        values = [counts[label] for label in labels]
        axis.plot(labels, values, marker="o", color="#2f6f73", linewidth=2)
        axis.set_title("Articles by Publish Date")
        axis.set_xlabel("Date")
        axis.set_ylabel("Articles")
        axis.tick_params(axis="x", labelrotation=35)
        axis.grid(axis="y", linestyle="--", alpha=0.35)
        figure.tight_layout()
        return figure

    def _bar_chart(
        self,
        counts: Counter,
        title: str,
        xlabel: str,
        ylabel: str,
    ) -> Figure:
        figure = Figure(figsize=self.figsize, dpi=100)
        axis = figure.add_subplot(111)

        if not counts:
            self._empty_chart(axis, "No articles available")
            return figure

        labels = list(counts.keys())
        values = [counts[label] for label in labels]
        axis.bar(labels, values, color="#2f6f73")
        axis.set_title(title)
        axis.set_xlabel(xlabel)
        axis.set_ylabel(ylabel)
        axis.tick_params(axis="x", labelrotation=30)
        axis.grid(axis="y", linestyle="--", alpha=0.35)
        figure.tight_layout()
        return figure

    def _empty_chart(self, axis: Any, message: str) -> None:
        axis.text(0.5, 0.5, message, ha="center", va="center")
        axis.set_axis_off()


def create_source_distribution_chart(articles: Iterable[Any]) -> Figure:
    return ArticleChartBuilder().source_distribution(articles)


def create_category_distribution_chart(articles: Iterable[Any]) -> Figure:
    return ArticleChartBuilder().category_distribution(articles)


def create_publication_timeline_chart(articles: Iterable[Any]) -> Figure:
    return ArticleChartBuilder().publication_timeline(articles)


def _clean_label(value: Any, fallback: str) -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _normalise_date(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    if "T" in text:
        text = text.split("T", 1)[0]

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text[:10], fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return text[:10]
