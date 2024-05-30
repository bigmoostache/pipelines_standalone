from custom_types.URL.type import URL
from gnews import GNews
import os 
from typing import List
from datetime import datetime

class Pipeline:
    def __init__(self,
                 has_in_title : str = "",
                 n_days: int = 30):
        self.n_days = f'{n_days}d'
        self.hasintitle = [_.strip() for _ in has_in_title.split(',') if _.strip()]
    
    def __call__(self, query: str) -> List[URL]:
        google_news = GNews(period=self.n_days)
        news = google_news.get_news(query)
        for _ in self.hasintitle:
            news = [__ for __ in news if _.lower() in __.get("title", "").lower()]
        date_format = '%a, %d %b %Y %H:%M:%S GMT'
        news = [URL(url = _['url'], title = _['title'], date = datetime.strptime(_['published date'], date_format).isoformat()) for _ in news]
        return news