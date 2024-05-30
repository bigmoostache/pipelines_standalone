from custom_types.JSONL.type import JSONL
class Pipeline:

    def __init__(self):
        pass

    def __call__(self, json : dict) -> JSONL:
        assert isinstance(json, list)
        return JSONL(json)