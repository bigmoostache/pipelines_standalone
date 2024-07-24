from typing import List
class Pipeline:
    def __init__(self,
                 param : str,
                 ):
        self.param = param
    def __call__(self, json : dict) -> List[str]:
        assert self.param in json
        assert isinstance(json[self.param], list)
        return [str(_) for _ in json[self.param]]
            
