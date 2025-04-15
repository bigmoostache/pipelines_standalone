import os
from typing import List, Literal
from custom_types.PROMPT.type import PROMPT
from pipelines.LLMS.v3.client import Pipeline as ClientPipeline, Providers

class Pipeline:
    def __init__(self,
        provider: Providers = "openai",
        model: str = "gpt-4.1"
        ):
        self.provider = provider
        self.model = model
    def __call__(self, 
                p : PROMPT,
                output_format : str
                ) -> str:
        # for now, str as output, but this will change
        if self.provider == "openai":
            return self.openai(p, output_format)
        elif self.provider == "azure":
            return self.azure(p, output_format)
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented")
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