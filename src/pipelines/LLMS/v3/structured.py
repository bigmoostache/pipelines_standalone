import os
from typing import List, Literal
from custom_types.PROMPT.type import PROMPT
from pipelines.LLMS.v3.client import Pipeline as ClientPipeline, Providers

from custom_types.trees.gap_analysis.type import ResponseType as Tree_Gap_AnalysisResponseType

output_formats = {
    'tree/gap_analysis': Tree_Gap_AnalysisResponseType,
}

class Pipeline:
    def __init__(self,
        provider: Providers = "openai",
        model: str = "gpt-4.1",
        hard_coded_model: Literal['none', 'tree/gap_analysis'] = 'none',
        convert_back_to_dict: bool = False
        ):
        self.provider = provider
        self.model = model
        self.hard_coded_model = hard_coded_model
        self.convert_back_to_dict = convert_back_to_dict
    def __call__(self, 
                p : PROMPT,
                output_format : str
                ) -> dict:
        if self.hard_coded_model != 'none':
            output_format = output_formats[self.hard_coded_model]
        # for now, str as output, but this will change
        if self.provider == "openai":
            response = self.openai(p, output_format)
        elif self.provider == "azure":
            response = self.azure(p, output_format)
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented")
        if self.convert_back_to_dict:
            response = response.model_dump()
        return response
    def openai(self, p : PROMPT, output_format: str) -> str:
        client = ClientPipeline(provider=self.provider, model=self.model)()
        response = client.beta.chat.completions.parse(
            model=self.model,
            messages=p.messages,
            response_format=output_format,
        )
        return response.choices[0].message.parsed
        
    def azure(self, p : PROMPT, output_format: str) -> str:
        client = ClientPipeline(provider=self.provider, model=self.model)()
        response = client.beta.chat.completions.parse(
                model=self.model,
                messages=p.messages,
                response_format=output_format,
            )
        return response.choices[0].message.parsed