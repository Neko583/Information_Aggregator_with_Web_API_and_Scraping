"""Web scraping package.

Author: Yuxiang Wang
Part of the news aggregator assignment (scraping and data processing scope).
"""

from .scraper import NewsScraper, ScrapedArticle

__all__ = ["NewsScraper", "ScrapedArticle"]
