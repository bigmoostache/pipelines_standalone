from typing import List
from custom_types.URL2.type import URL2

class Pipeline:
    def __init__(self, 
                 separator : str = "\n",
                 ):
        self.separator = separator 

    def __call__(self, urls: str) -> List[URL2]:
        urls = [_ for _ in urls.split(self.separator) if _]
        return [URL2.init(url = _) for _ in urls]