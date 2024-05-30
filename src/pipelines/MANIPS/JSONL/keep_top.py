
from custom_types.JSONL.type import JSONL


class Pipeline:
    def __init__(self, sort_on: str, keep : int = 10):
        self.sort_on = sort_on
        self.keep = keep

    def __call__(self, jsonl : JSONL) -> JSONL:
        values = jsonl.lines
        values.sort(key = lambda x : x.get(self.sort_on, 0))
        return JSONL(values[::-1][:self.keep][::-1])