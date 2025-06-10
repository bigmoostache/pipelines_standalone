from custom_types.GRID.type import GRID
from pipelines.LLMS.v3.structured import Pipeline as StructuredPipeline
from pipelines.LLMS.v3.client import Providers
from custom_types.PROMPT.type import PROMPT

class Pipeline:
    def __init__(self, 
                model: str = "gpt-4.1",
                provider: Providers = "openai"):
        self.model = model
        self.provider = provider
        
    def __call__(self,
                p : PROMPT,
                grid: GRID
                ) -> dict:
        output_type = grid.create_model(name='GRID')
        pipe = StructuredPipeline(
            provider=self.provider,
            model=self.model,
            hard_coded_model='none',
            convert_back_to_dict = True
        )
        return pipe(p, output_format=output_type, mode='structured')