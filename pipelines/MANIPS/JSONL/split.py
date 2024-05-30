from typing import List
from custom_types.JSONL.type import JSONL

class Pipeline:
    def __init__(self, split_on: str):
        self.split_on = split_on

    def __call__(self, jsonl : JSONL) -> List[JSONL]:
        values = list(set([d[self.split_on] for d in jsonl.lines]))
        res = {v:[d for d in jsonl.lines if d[self.split_on] == v] for v in values}
        res = [JSONL(lines = res[v]) for v in res]
        return res