from typing import List
from custom_types.URL.type import URL
from googleapiclient.discovery import build
import os 

class Pipeline:
    __env__ = ["GOOGLE_CX", "GOOGLE_SEARCH_API_KEY"]
    def __init__(self, n_days : int = 30):
        self.n_days = 30 

    def __call__(self, query: str) -> List[URL]:
        service = build(
                "customsearch", "v1", developerKey=os.environ.get("GOOGLE_SEARCH_API_KEY")
            )
        res = (
            service.cse()
            .list(
                q=query,
                cx=os.environ.get("GOOGLE_CX"),
                dateRestrict =f'd{self.n_days}'
            )
            .execute()
        )
        return [URL(url = _['link'], title=_['title']) for _ in res['items']]