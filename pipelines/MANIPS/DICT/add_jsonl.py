from custom_types.JSONL.type import JSONL
class Pipeline:
    def __init__(self,
                 param_name:str
                 ):
        self.param_name = param_name


    def __call__(self, value_to_add : JSONL, dic : dict) -> dict:
        dic[self.param_name] = value_to_add.lines
        return dic