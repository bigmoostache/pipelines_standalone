from custom_types.JSONL.type import JSONL

class Pipeline:
    def __init__(self,
                 param:str,
                 value : bool = False
                 ):
        self.param = param
        self.value = value
    
    def __call__(self, jsonl : JSONL) -> JSONL:
        for _ in jsonl.lines:
            _[self.param] = self.value
        return jsonl