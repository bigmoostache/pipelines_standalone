import json 
from custom_types.JSON.type import BytesEncoder
class Pipeline:
    def __init__(self):
        pass
    def __call__(self, dic : dict) -> str:
        return json.dumps(dic, indent = 2, cls=BytesEncoder)