
from custom_types.JSONL.type import JSONL


class Pipeline:
    def __init__(self, sort_on: str, keep : int = 10, reverse : bool = False):
        self.sort_on = sort_on
        self.keep = keep
        self.reverse = reverse

    def __call__(self, jsonl : JSONL) -> JSONL:
        values = jsonl.lines
        values.sort(key = lambda x : x.get(self.sort_on, 0), reverse = self.reverse)
        return JSONL(values[::-1][:self.keep][::-1])