from pipelines.LLMS.v3.structured import Pipeline as StructuredPipeline
from custom_types.PROMPT.type import PROMPT
from custom_types.framework_formats.TUTORIAL_DEMO.type import SimpleGraph
from pipelines.LLMS.v3.client import Providers

class Pipeline:
    def __init__(self, 
                 provider: Providers = "openai",
                 model : str = "gpt-4.1",
                 ):
        self.provider = provider
        self.model = model
    def __call__(self,
                 prompt: PROMPT) -> SimpleGraph:
        return StructuredPipeline(
            provider=self.provider, 
            model=self.model
        )(prompt, SimpleGraph)