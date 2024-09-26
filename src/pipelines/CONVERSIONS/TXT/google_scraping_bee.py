from typing import List
from custom_types.URL2.type import URL2
import os 
import requests
from datetime import datetime, timedelta
from typing import Literal
import time  # Import time module for sleep functionality

class Pipeline:
    __env__ = ["SCRAPING_BEE"]
    def __init__(self, 
                 timeframe : Literal["day", "week", "month", "year"] = "month",
                 news : bool = False,
                 n_results : int = 10
                 ):
        self.news = news
        self.n_results = n_results
        self.extraparams = {
            'day': '&tbs=qdr:d',
            'week': '&tbs=qdr:w',
            'month': '&tbs=qdr:m',
            'year': '&tbs=qdr:y'
        }.get(timeframe, '&tbs=qdr:m')

    def __call__(self, query: str) -> List[URL2]:
        SCRAPING_BEE = os.environ.get("SCRAPING_BEE")
        params = {
            'api_key': SCRAPING_BEE,
            'search': query,
            'language': 'en',
            'extra_params': self.extraparams,
            'nb_results': str(self.n_results),
        }
        if self.news:
            params['search_type'] = 'news'
        
        max_retries = 10  # Maximum number of retries
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(
                    url='https://app.scrapingbee.com/api/v1/store/google',
                    params=params
                )
                response.raise_for_status()
                break  # Exit loop if request is successful
            except requests.exceptions.HTTPError as e:
                if (e.response.status_code == 429 and
                    'TOO MANY REQUESTS' in str(e)):
                    retries += 1
                    time.sleep(5)  # Wait for 5 seconds before retrying
                    continue  # Retry the request
                elif e.response.status_code == 504: # Gateway Timeout
                    retries += 1
                    time.sleep(5)
                else:
                    raise
        else:
            # If max retries exceeded, raise an exception
            raise Exception("Maximum retries exceeded for 429 TOO MANY REQUESTS error.")

        result = response.json()
        news = result['news_results'] if self.news else result['organic_results']
        res = []
        for item in news:
            date = item.get('date', '')
            url = item['link'] if self.news else item['url']
            title = item['title']
            res.append(URL2.init(url=url, title=title, date=date))
        return res
