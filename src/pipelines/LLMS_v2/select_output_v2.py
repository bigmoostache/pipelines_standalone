from custom_types.PROMPT.type import PROMPT
from custom_types.SELECT.type import SELECT
import os
from pipelines.LLMS.v3.structured import Providers

class Pipeline:
    def __init__(self, 
                 model : str = "gpt-4o",
                 provider: Providers = 'openai',
                 rerolls: int = 1
                 ):
        self.model = model
        self.provider = provider
        
    def __call__(self, 
             p : PROMPT,
             e : SELECT
             ) -> dict:
        p.truncate()
        return e(
            p, 
            model=self.model,
            provider=self.provider)