from custom_types.JSONL.type import JSONL
from typing import List
class Pipeline:

    def __init__(self, key : str):
        self.key = key
    def __call__(self, texts : List[str]) -> JSONL:
        texts = [{self.key : _} for _ in texts]
        return JSONL(texts)