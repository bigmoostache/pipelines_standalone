from custom_types.PROMPT.type import PROMPT
from custom_types.SELECT.type import SELECT
import openai
import os
from pipelines.LLMS.v3.structured import Providers, Pipeline as StructuredPipeline

class Pipeline:
    def __init__(self, 
                provider: Providers = "openai",
                model: str = "gpt-4.1",
                temperature : float =1, 
                top_p : float =1
                ):
        self.provider = provider
        self.model = model
        
    def __call__(self, 
                 p : PROMPT,
                 ) -> SELECT:
        return StructuredPipeline(
            provider=self.provider, 
            model=self.model, 
            hard_coded_model='select'
        )(p, None, 'structured')
    