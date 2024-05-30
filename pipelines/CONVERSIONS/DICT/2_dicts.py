from typing import List
class Pipeline:
    def __init__(self,
                 param : str = "",
                 ):
        self.param = param
    def __call__(self, json : dict) -> List[dict]:
        if self.param:
            assert self.param in json
            json = json[self.param]
        assert isinstance(json, list)
        return json