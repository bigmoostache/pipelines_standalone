
from custom_types.JSONL.type import JSONL
class Pipeline:
    def __init__(self,
                 jsonl_param:str
                 ):
        self.jsonl_param = jsonl_param
        
    def __call__(self, jsonl : JSONL) -> JSONL:
        used = set()
        res = []
        for l in jsonl.lines:
            v = l.get(self.jsonl_param)
            if v in used:
                continue 
            used.add(v)
            res.append(l)
        return JSONL(res)