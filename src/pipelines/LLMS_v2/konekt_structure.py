import os
from custom_types.PROMPT.type import PROMPT
from custom_types.KONEKT.type import GET_STRUCTURE_FROM_LLM, GenericType

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self, 
                 model : str = "gpt-4o-2024-08-06"):
        self.model = model
    def __call__(self, 
                 p : PROMPT
                 ) -> GenericType:
        api_key = os.environ.get("openai_api_key")
        return GET_STRUCTURE_FROM_LLM(p, api_key, self.model)
