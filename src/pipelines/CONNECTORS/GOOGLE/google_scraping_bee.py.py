from typing import List
from custom_types.URL.type import URL
import os 
import requests
from datetime import datetime, timedelta


class Pipeline:
    __env__ = ["SCRAPING_BEE"]
    def __init__(self, 
                 n_days : int = 30,
                 news : bool = False,
                 ):
        self.n_days = 30 
        self.news = news

    def __call__(self, query: str) -> List[URL]:
        SCRAPING_BEE = os.environ.get("SCRAPING_BEE")
        params={
                'api_key': SCRAPING_BEE,
                'search': query,
                'language': 'en'
            }
        if self.news:
            params['search_type'] = 'news'
        response = requests.get(
            url='https://app.scrapingbee.com/api/v1/store/google',
            params=params
        )
        result.raise_for_status()
        result = response.json()
        news = result['news_results'] if self.news else result['organic_results']
        res = []
        date_filter = datetime.now() - timedelta(days=self.n_days)
        for _ in news:
            date = _['date'] if _['date'] else ''
            if date and datetime.fromisoformat(date) < date_filter:
                continue
            url = _['url'] if not self.news else _['link']
            title = _['title']
            res.append(URL(url = url, title=title, date=date))
        return res
        