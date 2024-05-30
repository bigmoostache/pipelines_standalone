import json
from custom_types.JSONL.type import JSONL
from custom_types.JSON.type import BytesEncoder

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, jsonl : JSONL) -> str:
        return json.dumps(jsonl.lines, indent =2, cls=BytesEncoder)