from custom_types.JSONL.type import JSONL

class Pipeline:
    def __init__(self,
                 param:str,
                 keep_false : bool = False
                 ):
        self.param = param
        self.keep_false = keep_false
    
    def __call__(self, jsonl : JSONL) -> JSONL:
        print(jsonl.lines[0])
        if self.keep_false:
            return JSONL([_ for _ in jsonl.lines if not _[self.param]])
        return JSONL([_ for _ in jsonl.lines if _[self.param]])