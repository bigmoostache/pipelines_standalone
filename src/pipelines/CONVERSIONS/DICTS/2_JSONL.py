from typing import List 
from custom_types.JSONL.type import JSONL

class Pipeline:
    def __init__(self,
                 sort_on:str = ""
                 ):
        self.sort_on = sort_on
        
    def __call__(self, dicts : List[dict]) -> JSONL:
        if self.sort_on:
            dicts.sort(key=lambda x : x.get(self.sort_on, 0))
        return JSONL(dicts)