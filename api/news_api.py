# api/news_api.py
import requests
from models.article import Article
from config import API_KEY, BASE_URL, DEFAULT_ARTICLE_LIMIT


class NewsAPIClient:
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key
        self.base_url = BASE_URL

    def get_top_headlines(self, category="general", limit=DEFAULT_ARTICLE_LIMIT):
        url = self.base_url + "top-headlines"
        params = {
            "apiKey": self.api_key,
            "category": category,
            "language": "en",
            "pageSize": limit
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            if data["status"] != "ok":
                print(f"API error: {data.get('message', 'Unknown error')}")
                return []

            return self._parse_articles(data["articles"])

        except requests.exceptions.ConnectionError:
            print("Network connection failed. Please check your network connection.")
            return []
        except requests.exceptions.Timeout:
            print("The request timed out. Please try again later.")
            return []
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            return []

    def search_articles(self, keyword, limit=DEFAULT_ARTICLE_LIMIT):
        url = self.base_url + "everything"
        params = {
            "apiKey": self.api_key,
            "q": keyword,
            "language": "en",
            "pageSize": limit,
            "sortBy": "publishedAt"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            if data["status"] != "ok":
                print(f"API error: {data.get('message', 'Unknown error')}")
                return []

            return self._parse_articles(data["articles"])

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []

    def _parse_articles(self, raw_articles):
        articles = []

        for item in raw_articles:
            article = Article(
                title=item.get("title") or "Untitled",
                source=item.get("source", {}).get("name") or "Unknown source",
                author=item.get("author") or "Author unknown",
                published_at=item.get("publishedAt") or "Unknown time",
                url=item.get("url") or "",
                description=item.get("description") or ""
            )
            articles.append(article)

        return articles