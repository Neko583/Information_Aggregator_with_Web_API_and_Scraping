
import tkinter as tk
from tkinter import messagebox

# A
from api.news_api import NewsAPIClient
from models.article import Article

# B
from processor.data_processor import DataProcessor
from scraper.scraper import NewsScraper

# C
from visualization.charts import ArticleChartBuilder
from gui.gui import NewsAggregatorGUI


class NewsAggregatorApp:
    def __init__(self):
        self.root = tk.Tk()

        self.api_client = NewsAPIClient()

        self.data_processor = DataProcessor()
        self.scraper = NewsScraper()

        self.chart_builder = ArticleChartBuilder()
        self.gui = NewsAggregatorGUI(self.root, fetch_callback=self.get_news_full_process)

    def get_news_full_process(self, category="general", limit=3):
        try:
            raw_articles = self.api_client.get_top_headlines(category=category, limit=limit)
            if not raw_articles:
                return []

            cleaned = self.data_processor.clean_articles(raw_articles)
            urls = [a["url"] for a in cleaned if a.get("url")]
            scraped = self.scraper.scrape_many(urls)
            merged = self.data_processor.merge_with_scraped(cleaned, scraped)
            final_news = self.data_processor.remove_duplicates(merged)

            return final_news
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch news: {str(e)}")
            return []

    def search_news(self, keyword, limit=3):
        try:
            raw = self.api_client.search_articles(keyword, limit)
            cleaned = self.data_processor.clean_articles(raw)
            urls = [a["url"] for a in cleaned if a.get("url")]
            scraped = self.scraper.scrape_many(urls)
            merged = self.data_processor.merge_with_scraped(cleaned, scraped)
            return self.data_processor.remove_duplicates(merged)
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
            return []

    def generate_charts(self, articles):
        return {
            "source": self.chart_builder.source_distribution(articles),
            "category": self.chart_builder.category_distribution(articles),
            "timeline": self.chart_builder.publication_timeline(articles)
        }

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = NewsAggregatorApp()
        app.run()
    except Exception as e:
        print(f"Program error: {e}")