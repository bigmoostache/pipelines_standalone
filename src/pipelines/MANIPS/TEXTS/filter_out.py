import re
from typing import List

class Pipeline:

    def __init__(self, keywords: str):
        self.keywords = keywords.split(',')
        self.keywords = [keyword.strip() for keyword in self.keywords]

    def __call__(self, chunks : List[str]) -> List[str]:
        return [chunk for chunk in chunks if not any([keyword in chunk for keyword in self.keywords])]