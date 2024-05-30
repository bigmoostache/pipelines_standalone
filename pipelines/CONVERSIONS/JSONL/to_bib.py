from typing import List 
from pipelines.CONVERSIONS.DICT.to_bib import Pipeline as dict_to_bib
from custom_types.BIB.type import BIB
from custom_types.JSONL.type import JSONL

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, jsonl : JSONL) -> List[BIB]:
        p = dict_to_bib()
        return [p(_) for _ in jsonl.lines]