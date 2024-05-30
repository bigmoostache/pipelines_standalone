from custom_types.JSONL.type import JSONL
from typing import List
class Pipeline:
    def __init__(self,
                 ):
        pass
        
    def __call__(self, jsonl : JSONL, dic: dict) -> List[dict]:
        return [{**_, **dic} for _ in jsonl.lines]