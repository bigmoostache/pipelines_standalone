from typing import List 
from custom_types.JSONL.type import JSONL

class Pipeline:

    def __init__(self):
        pass

    def __call__(self, jsonl : List[JSONL]) -> JSONL:
        all_lines = [y for x in jsonl for y in x.lines]
        return JSONL(all_lines)
