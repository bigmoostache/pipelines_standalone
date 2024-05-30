
from custom_types.JSONL.type import JSONL
class Pipeline:
    def __init__(self, sort_on : str):
        self.sort_on = sort_on

    def __call__(self, jsons : JSONL) -> JSONL:
        return JSONL(sorted(jsons.lines, key=lambda x: x[self.sort_on]))