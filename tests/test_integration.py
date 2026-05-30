import unittest
from unittest.mock import patch

from main import NewsAggregatorApp

class TestMainIntegration(unittest.TestCase):

    @patch("gui.gui.NewsAggregatorGUI")
    def test_main_init(self, mock_gui):
        app = NewsAggregatorApp()
        self.assertIsNotNone(app.api_client)
        self.assertIsNotNone(app.data_processor)

    @patch("gui.gui.NewsAggregatorGUI")
    @patch("main.NewsAPIClient.get_top_headlines")
    def test_news_pipeline(self, mock_api, mock_gui):
        mock_api.return_value = []
        app = NewsAggregatorApp()
        res = app.get_news_full_process("tech", 1)
        self.assertIsInstance(res, list)

    @patch("gui.gui.NewsAggregatorGUI")
    @patch("main.NewsAPIClient.search_articles")
    def test_search(self, mock_search, mock_gui):
        mock_search.return_value = []
        app = NewsAggregatorApp()
        res = app.search_news("ai", 1)
        self.assertIsInstance(res, list)

    @patch("gui.gui.NewsAggregatorGUI")
    def test_charts(self, mock_gui):
        app = NewsAggregatorApp()
        charts = app.generate_charts([])
        self.assertIsInstance(charts, dict)

if __name__ == '__main__':
    unittest.main(verbosity=2)