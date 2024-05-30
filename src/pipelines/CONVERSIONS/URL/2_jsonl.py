from custom_types.JSONL.type import JSONL
from custom_types.URL.type import URL
from typing import List
class Pipeline:
    def __init__(self):
        pass

    def __call__(self, urls : List[URL]) -> JSONL:
        return JSONL([url.__dict__ for url in urls])