
from custom_types.JSONL.type import JSONL

    
class Pipeline:
    def __init__(self,
                 dic_param:str,
                 jsonlparam:str
                 ):
        self.dic_param = dic_param
        self.jsonlparam = jsonlparam
        


    def __call__(self, jsonl : JSONL, dic:  dict) -> JSONL:
        return JSONL([_ for _ in jsonl.lines if dic[self.dic_param] in _.get(self.jsonlparam, [])])