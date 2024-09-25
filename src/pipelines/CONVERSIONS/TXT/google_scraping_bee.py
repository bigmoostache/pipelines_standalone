from typing import List
from custom_types.URL2.type import URL2
import os 
import requests
from datetime import datetime, timedelta
from typing import Literal


class Pipeline:
    __env__ = ["SCRAPING_BEE"]
    def __init__(self, 
                 timeframe : Literal["day", "week", "month", "year"] = "month",
                 news : bool = False,
                 n_results : int = 10
                 ):
        self.news = news
        self.n_results = n_results
        self.extraparams = {'day':'&tbs=qdr:d', 'week':'&tbs=qdr:w', 'month':'&tbs=qdr:m', 'year':'&tbs=qdr:y'}.get(timeframe, '&tbs=qdr:m')

    def __call__(self, query: str) -> List[URL2]:
        SCRAPING_BEE = os.environ.get("SCRAPING_BEE")
        params={
                'api_key': SCRAPING_BEE,
                'search': query,
                'language': 'en',
                'extra_params': self.extraparams,
                'nb_results': str(self.n_results),
            }
        if self.news:
            params['search_type'] = 'news'
        response = requests.get(
            url='https://app.scrapingbee.com/api/v1/store/google',
            params=params
        )
        response.raise_for_status()
        result = response.json()
        news = result['news_results'] if self.news else result['organic_results']
        res = []
        for _ in news:
            date = _['date'] if _['date'] else ''
            url = _['url'] if not self.news else _['link']
            title = _['title']
            res.append(URL2.init(url = url, title=title, date=date))
        return res