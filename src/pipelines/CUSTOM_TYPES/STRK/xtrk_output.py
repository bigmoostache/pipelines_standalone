from custom_types.PROMPT.type import PROMPT
from custom_types.XTRK.type import DataStructure
from pipelines.LLMS.v3.client import Providers
from pipelines.LLMS.v3.structured import Pipeline as StructuredPipeline

class Pipeline:
    def __init__(self,
                provider: Providers = "openai",
                model : str = "gpt-4o-2024-08-06"):
        self.pipeline = StructuredPipeline(
            provider=provider, 
            model=model, 
            hard_coded_model='xtrk'
        )
    def __call__(self, 
                p : PROMPT
                ) -> DataStructure:
        return self.pipeline(p, '', 'structured')