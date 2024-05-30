from custom_types.JSONL.type import JSONL
class Pipeline:

    def __init__(self, list_name:str, wrap_param: bool = False):
        self.param = list_name
        self.wrap = wrap_param

    def __call__(self, json : dict) -> JSONL:
        json = json.get(self.param) if self.param else json
        assert isinstance(json, list)
        if self.wrap:
            json = [{self.param:_} for _ in json]
        return JSONL(json)