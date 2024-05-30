from typing import List 
from custom_types.JSONL.type import JSONL
from custom_types.URL.type import URL

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, jsonl : JSONL) -> List[URL]:
        return [URL(**_) for _ in jsonl.lines]