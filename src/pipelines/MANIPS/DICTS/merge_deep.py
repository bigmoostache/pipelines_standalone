import re
from typing import List
from custom_types.JSONL.type import JSONL

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, dics : List[dict]) -> JSONL:
        keys = list(set([__ for _ in dics for __ in _.keys()]))
        res = {k:{'__NAME__':k} for k in keys}
        for d in dics:
            for k,v in d.items():
                res[k] = {**res[k], **v}
        return JSONL([v for k,v in res.items()])
        