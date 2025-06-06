from typing import List
from custom_types.XLSX.type import XLSX
import pandas as pd
from pipelines.MANIPS.XLSX.table_to_tables import Schema
from pipelines.LLMS.v3.structured import Pipeline as StructuredPipeline
from pipelines.LLMS.v3.client import Providers
from custom_types.PROMPT.type import PROMPT

class Pipeline:
    def __init__(self, 
                model: str = "gpt-4.1",
                provider: Providers = "openai",
                name: str = 'dynamic_schema'):
        self.name = name
        self.model = model
        self.provider = provider
        
    def __call__(self,
                p : PROMPT,
                schema: dict
                ) -> dict:
        schema = Schema.model_validate(schema)
        output_type = schema.create_dynamic_model(self.name)
        pipe = StructuredPipeline(
            provider=self.provider,
            model=self.model,
            hard_coded_model='none',
            convert_back_to_dict = True
            )
        p = pipe(p, output_format=output_type, mode='structured')
        return p