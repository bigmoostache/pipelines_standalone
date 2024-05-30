from custom_types.BIB.type import BIB
from custom_types.JSONL.type import JSONL

from typing import List

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, bib : List[BIB]) -> JSONL:
        return JSONL([b.__dict__ for b in bib])