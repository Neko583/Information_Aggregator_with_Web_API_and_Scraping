"""Tkinter user interface for the news information aggregator.

Module C is responsible for giving users a simple way to fetch articles,
inspect details, and view Matplotlib summaries.  The ``ArticlePresenter`` class
keeps formatting logic testable without needing to open a Tkinter window.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable, Iterable, Optional

from visualization.charts import (
    ArticleChartBuilder,
    article_to_dict,
)


CATEGORIES = (
    "general",
    "business",
    "entertainment",
    "health",
    "science",
    "sports",
    "technology",
)


class ArticlePresenter:
    """Prepare article records for list and detail display."""

    def __init__(self, articles: Optional[Iterable[Any]] = None) -> None:
        self.articles: list[dict] = []
        if articles is not None:
            self.set_articles(articles)

    def set_articles(self, articles: Iterable[Any]) -> None:
        self.articles = [article_to_dict(article) for article in articles]

    def list_label(self, index: int) -> str:
        article = self.articles[index]
        title = self._field(article, "title", "Untitled")
        source = self._field(article, "source", "Unknown source")
        date = self._field(article, "publish_date", "No date")
        return f"{index + 1}. {title} ({source}, {date})"

    def detail_text(self, index: int) -> str:
        article = self.articles[index]
        title = self._field(article, "title", "Untitled")
        source = self._field(article, "source", "Unknown source")
        author = self._field(article, "author", "Unknown author")
        date = self._field(article, "publish_date", "No date")
        url = self._field(article, "url", "No URL")
        description = self._field(article, "description", "")
        content = self._field(article, "content", "")

        sections = [
            f"Title: {title}",
            f"Source: {source}",
            f"Author: {author}",
            f"Published: {date}",
            f"URL: {url}",
        ]
        if description:
            sections.append(f"\nDescription:\n{description}")
        if content:
            sections.append(f"\nContent:\n{content}")
        return "\n".join(sections)

    def labels(self) -> list[str]:
        return [self.list_label(index) for index in range(len(self.articles))]

    def _field(self, article: dict, key: str, fallback: str) -> str:
        value = article.get(key)
        if value is None and key == "publish_date":
            value = article.get("published_at")
        if value is None:
            return fallback
        text = str(value).strip()
        return text or fallback


class NewsAggregatorGUI:
    """Main Tkinter window for browsing and visualising articles."""

    def __init__(
        self,
        root: tk.Tk,
        fetch_callback: Optional[Callable[[str, int], list[Any]]] = None,
    ) -> None:
        self.root = root
        self.root.title("News Information Aggregator")
        self.root.geometry("1100x720")

        self.fetch_callback = fetch_callback or self._fetch_from_api
        self.presenter = ArticlePresenter()
        self.chart_builder = ArticleChartBuilder()
        self.chart_canvas = None

        self.category_var = tk.StringVar(value=CATEGORIES[0])
        self.limit_var = tk.IntVar(value=10)
        self.status_var = tk.StringVar(value="Ready")

        self._build_layout()

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(1, weight=1)

        controls = ttk.Frame(self.root, padding=12)
        controls.grid(row=0, column=0, columnspan=2, sticky="ew")
        controls.columnconfigure(7, weight=1)

        ttk.Label(controls, text="Category").grid(row=0, column=0, padx=(0, 6))
        category_box = ttk.Combobox(
            controls,
            textvariable=self.category_var,
            values=CATEGORIES,
            state="readonly",
            width=16,
        )
        category_box.grid(row=0, column=1, padx=(0, 12))

        ttk.Label(controls, text="Articles").grid(row=0, column=2, padx=(0, 6))
        limit_box = ttk.Spinbox(
            controls,
            from_=1,
            to=50,
            textvariable=self.limit_var,
            width=6,
        )
        limit_box.grid(row=0, column=3, padx=(0, 12))

        ttk.Button(controls, text="Fetch News", command=self.fetch_articles).grid(
            row=0, column=4, padx=(0, 8)
        )
        ttk.Button(controls, text="Clear", command=self.clear_articles).grid(
            row=0, column=5, padx=(0, 8)
        )
        ttk.Button(
            controls,
            text="Source Chart",
            command=lambda: self.show_chart("source"),
        ).grid(row=0, column=6, padx=(0, 8))
        ttk.Button(
            controls,
            text="Category Chart",
            command=lambda: self.show_chart("category"),
        ).grid(row=0, column=7, sticky="w")

        left = ttk.Frame(self.root, padding=(12, 0, 6, 12))
        left.grid(row=1, column=0, sticky="nsew")
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        ttk.Label(left, text="Articles").grid(row=0, column=0, sticky="w")
        self.article_list = tk.Listbox(left, height=22, exportselection=False)
        self.article_list.grid(row=1, column=0, sticky="nsew")
        self.article_list.bind("<<ListboxSelect>>", self.display_selected_article)

        list_scroll = ttk.Scrollbar(
            left,
            orient="vertical",
            command=self.article_list.yview,
        )
        list_scroll.grid(row=1, column=1, sticky="ns")
        self.article_list.configure(yscrollcommand=list_scroll.set)

        right = ttk.Frame(self.root, padding=(6, 0, 12, 12))
        right.grid(row=1, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.rowconfigure(3, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="Article Details").grid(row=0, column=0, sticky="w")
        self.detail_text = tk.Text(right, wrap="word", height=13)
        self.detail_text.grid(row=1, column=0, sticky="nsew")

        ttk.Label(right, text="Visualization").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.chart_frame = ttk.Frame(right)
        self.chart_frame.grid(row=3, column=0, sticky="nsew")
        self.chart_frame.columnconfigure(0, weight=1)
        self.chart_frame.rowconfigure(0, weight=1)

        status = ttk.Label(self.root, textvariable=self.status_var, padding=(12, 4))
        status.grid(row=2, column=0, columnspan=2, sticky="ew")

    def fetch_articles(self) -> None:
        category = self.category_var.get()
        limit = max(1, int(self.limit_var.get()))
        self.status_var.set(f"Fetching {limit} {category} articles...")
        self.root.update_idletasks()

        try:
            articles = self.fetch_callback(category, limit)
        except Exception as exc:
            messagebox.showerror("Fetch failed", str(exc))
            self.status_var.set("Fetch failed")
            return

        self.set_articles(articles)
        self.status_var.set(f"Loaded {len(self.presenter.articles)} articles")

    def set_articles(self, articles: Iterable[Any]) -> None:
        self.presenter.set_articles(articles)
        self.article_list.delete(0, tk.END)
        for label in self.presenter.labels():
            self.article_list.insert(tk.END, label)

        self.detail_text.delete("1.0", tk.END)
        if self.presenter.articles:
            self.article_list.selection_set(0)
            self.display_selected_article()
            self.show_chart("source")
        else:
            self._clear_chart()

    def clear_articles(self) -> None:
        self.set_articles([])
        self.status_var.set("Cleared")

    def display_selected_article(self, _event: Any = None) -> None:
        selection = self.article_list.curselection()
        if not selection:
            return

        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert(tk.END, self.presenter.detail_text(selection[0]))

    def show_chart(self, chart_type: str) -> None:
        if chart_type == "category":
            figure = self.chart_builder.category_distribution(self.presenter.articles)
        else:
            figure = self.chart_builder.source_distribution(self.presenter.articles)
        self._render_chart(figure)

    def _render_chart(self, figure: Any) -> None:
        self._clear_chart()
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except Exception:
            ttk.Label(
                self.chart_frame,
                text="Matplotlib Tk backend is not available.",
            ).grid(row=0, column=0, sticky="nsew")
            return

        self.chart_canvas = FigureCanvasTkAgg(figure, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def _clear_chart(self) -> None:
        if self.chart_canvas is not None:
            self.chart_canvas.get_tk_widget().destroy()
            self.chart_canvas = None
        for child in self.chart_frame.winfo_children():
            child.destroy()

    def _fetch_from_api(self, category: str, limit: int) -> list[Any]:
        from api.news_api import NewsAPIClient

        client = NewsAPIClient()
        return client.get_top_headlines(category=category, limit=limit)


def run_app(fetch_callback: Optional[Callable[[str, int], list[Any]]] = None) -> None:
    root = tk.Tk()
    NewsAggregatorGUI(root, fetch_callback=fetch_callback)
    root.mainloop()


if __name__ == "__main__":
    run_app()
