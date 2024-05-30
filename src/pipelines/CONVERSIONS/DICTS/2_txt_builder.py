from typing import List 

class Pipeline:
    def __init__(self,
                 parameter : str,
                 sort_on:str = "index",
                 joiner:str = "\n"
                 ):
        self.joiner = joiner
        self.parameter = parameter
        self.sort_on = sort_on
        
    def __call__(self, dicts : List[dict]) -> str:
        dicts = sorted(dicts, key=lambda x: int(x.get(self.sort_on, 0)))
        return self.joiner.join([_.get(self.parameter, "").strip() for _ in dicts])