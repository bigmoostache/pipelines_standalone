
from custom_types.JSONL.type import JSONL    
class Pipeline:
    def __init__(self, new_index_name : str):
        self.idx = new_index_name

    def __call__(self, jsonl : JSONL) -> JSONL:
        return JSONL([{**_, self.idx:i+1} for i,_ in enumerate(jsonl.lines)])
        