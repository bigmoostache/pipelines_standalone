from typing import List 
from custom_types.JSONL.type import JSONL

class Pipeline:

    def __init__(self):
        pass

    def __call__(self, jsonl : JSONL) -> List[dict]:
        return jsonl.lines