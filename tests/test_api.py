# tests/test_api.py
import unittest
from unittest.mock import patch, MagicMock
from api.news_api import NewsAPIClient
from models.article import Article


class TestArticleModel(unittest.TestCase):
    def test_article_creation(self):
        article = Article(
            title="Test Title",
            source="BBC",
            author="John",
            published_at="2024-01-01",
            url="http://example.com"
        )
        self.assertEqual(article.title, "Test Title")
        self.assertEqual(article.source, "BBC")

    def test_article_to_dict(self):
        article = Article("Title", "CNN", "Jane", "2024-01-01", "http://example.com")
        result = article.to_dict()
        self.assertIsInstance(result, dict)
        self.assertIn("title", result)
        self.assertIn("url", result)

    def test_article_str(self):
        article = Article("My News", "BBC", "Tom", "2024-06-01", "http://test.com")
        output = str(article)
        self.assertIn("BBC", output)
        self.assertIn("My News", output)


class TestNewsAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = NewsAPIClient(api_key="fake_test_key")

    @patch("api.news_api.requests.get")
    def test_get_top_headlines_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "Test Article",
                    "source": {"name": "BBC"},
                    "author": "Test Author",
                    "publishedAt": "2024-01-01T00:00:00Z",
                    "url": "http://test.com",
                    "description": "Test description"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        articles = self.client.get_top_headlines(category="technology", limit=1)

        self.assertEqual(len(articles), 1)
        self.assertIsInstance(articles[0], Article)
        self.assertEqual(articles[0].title, "Test Article")

    @patch("api.news_api.requests.get")
    def test_get_top_headlines_returns_empty_on_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "error",
            "message": "Invalid API key"
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        articles = self.client.get_top_headlines()
        self.assertEqual(articles, [])

    @patch("api.news_api.requests.get")
    def test_article_limit(self, mock_get):
        fake_articles = [
            {"title": f"Article {i}", "source": {"name": "CNN"},
             "author": None, "publishedAt": "2024-01-01",
             "url": f"http://test{i}.com", "description": ""}
            for i in range(5)
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "ok", "articles": fake_articles}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        articles = self.client.get_top_headlines(limit=5)
        self.assertEqual(len(articles), 5)


if __name__ == "__main__":
    unittest.main()