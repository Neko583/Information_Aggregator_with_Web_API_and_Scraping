# Information_Aggregator_with_Web_API_and_Scraping

## Authors
Group G5:
- Module A [Yan Hao] 
- Module B [Yuxiang Wang] 
- Module C [Yanzhen Huang] 
- Module D [Wenze Qiao] 

## Description
Develop a Python program that aggregates news articles from different sources using both web APIs
and web scraping techniques. This assignment will cover skills related to making API requests,
handling JSON/XML data, and extracting information from HTML. It provides students with hands-on
experience in integrating data from both web APIs and web scraping, offering a practical
understanding of data aggregation from multiple sources.


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

### Features
- Tkinter desktop GUI for browsing aggregated news articles.
- Category dropdown and article limit input for user-controlled fetching.
- Article list panel plus detail view showing title, source, author, date, URL, description, and content.
- Matplotlib charts for article distribution by source and by category.
- Testable presentation and chart helper classes so GUI-related logic can be checked without opening a window.

### Run the GUI
From the project root directory:
```bash
python -m gui.gui
```

### Run Module C Tests
```bash
python -m unittest tests.test_gui
```

## Module D
### Features
- Developed `main.py`, connects API, data processing, web scraping, visualization, and GUI.
- Implemented full news processing pipeline, search function, and chart generation.
- Wrote `test_integration.py` to validate system stability and inter-module cooperation.
### Run Integration Tests
```bash
python -m unittest tests/test_integration.py -v
```
Expected result: **4 passed**
