from typing import List 
from custom_types.JSONL.type import JSONL
from custom_types.URL2.type import URL2

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, jsonl : JSONL) -> List[URL2]:
        return [URL2.parse_obj(_) for _ in jsonl.lines]