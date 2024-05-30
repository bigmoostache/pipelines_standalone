
from custom_types.JSONL.type import JSONL    
class Pipeline:
    def __init__(self, jsonl_param:str, new_param_name : str):
        self.jsonl_param = jsonl_param
        self.new_param_name = new_param_name

    def __call__(self, jsonl : JSONL, dic : dict) -> JSONL:
        for x in jsonl.lines:
            v = x.get(self.jsonl_param, None)
            if not v:
                continue 
            if v not in dic:
                continue 
            x[self.new_param_name] = dic.get(v)
        return jsonl
        