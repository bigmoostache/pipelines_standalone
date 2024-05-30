
from custom_types.JSONL.type import JSONL

class Pipeline:
    def __init__(self,
                 hash_param : str
                 ):
        self.hash_param = hash_param
        
    def __call__(self, jsonl : JSONL) -> JSONL:
        to_keep = []
        seen_hashes = set()
        for d in jsonl.lines:
            if d.get(self.hash_param, None) not in seen_hashes:
                to_keep.append(d)
                seen_hashes.add(d[self.hash_param])
        return JSONL(lines = to_keep)