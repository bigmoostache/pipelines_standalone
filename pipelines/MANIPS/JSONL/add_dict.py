
from custom_types.JSONL.type import JSONL
class Pipeline:
    def __init__(self):
        pass

    def __call__(self, jsonl : JSONL, dic : dict) -> JSONL:
        return JSONL([{**dic, **_} for _ in jsonl.lines])
        