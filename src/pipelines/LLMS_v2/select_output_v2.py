from custom_types.PROMPT.type import PROMPT
from custom_types.SELECT.type import SELECT
import os 

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self, 
                 model : str = "gpt-4o", 
                 rerolls: int = 1,
                 ):
        self.model = model
        self.rerolls = rerolls
        
    def __call__(self, 
             p : PROMPT,
             e : SELECT
             ) -> dict:
        p.truncate()
        return e(p.messages, openai_api_key=os.environ.get("openai_api_key"), model=self.model, rerolls=self.rerolls)