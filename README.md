# Information_Aggregator_with_Web_API_and_Scraping

## Authors
Group 2:
- Module A [Yan Hao] (25976440) 
- Module B [Student B Name] (Student B ID) 
- Module C [Student C Name] (Student C ID) 
- Module D [Student D Name] (Student D ID)

## Description

## Project Structure
```
Information_Aggregator_with_Web_API_and_Scraping/
├── main.py                       # Main application (Module D)
├── api/
│   └── news_api.py               # News API (Module A)
├── gui/
│   └── gui.py                    # (Module C)
├── models/
│   └── article.py                # Article class (Module A)
├── processor/
│   └── data_processor.py         # (Module B)
├── scraper/
│   └── scraper.py                # (Module B)
├── visualization/
│   └── charts.py                 # (Module C)
├── tests/
│   ├── test_api.py                
│   ├── test_integration.py        
│   ├── test_gui.py                
│   └── test_scraper.py           
├── .env                          # env
├── config.py                     # config
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```
## Module A

### Features
- Fetch latest news headlines from NewsAPI
- Support filtering news by category
- Support searching news by keywords
- Use Article class to encapsulate news data for other modules
- Built-in error handling to avoid program crashes
### API Key Configuration

1. Register a free account at https://newsapi.org
2. Log in and get your personal API Key
3. Configure in `.env` file (recommended):
```
API_KEY=Paste your API Key here
BASE_URL=https://newsapi.org/v2/
DEFAULT_ARTICLE_LIMIT=10
```
Or set directly in `config.py`:
```python
API_KEY = "Paste your API Key here"
BASE_URL = "https://newsapi.org/v2/"
DEFAULT_ARTICLE_LIMIT = 10
```

---

### Run Unit Tests
Execute the command in project root directory:
```bash
python -m pytest tests/test_api.py -v
```
Expected result: **6 passed**

---

### Quick API Test
Run the script below to verify functions:
```python
from api.news_api import NewsAPIClient

client = NewsAPIClient()
articles = client.get_top_headlines(category="technology", limit=5)
for article in articles:
    print(article)
```

---


## Module B

## Module C

## Module D
