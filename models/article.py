# models/article.py
from datetime import datetime

class Article:
    def __init__(self, title, source, author, published_at, url, description="", content=""):
        self.title = title
        self.source = source
        self.author = author
        self.published_at = published_at
        self.url = url
        self.description = description
        self.content = content

    def to_dict(self):
        return {
            "title": self.title,
            "source": self.source,
            "author": self.author,
            "published_at": self.published_at,
            "url": self.url,
            "description": self.description,
            "content": self.content
        }

    def __str__(self):
        return f"[{self.source}] {self.title} — {self.published_at}"