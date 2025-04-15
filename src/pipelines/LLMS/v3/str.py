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
                p : PROMPT) -> str:
        # for now, str as output, but this will change
        if self.provider == "openai":
            return self.openai(p)
        elif self.provider == "azure":
            return self.azure(p)
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented")
    def openai(self, p : PROMPT) -> str:
        client = ClientPipeline(provider=self.provider, model=self.model)()
        response = client.chat.completions.create(
            model=self.model,
            messages=p.messages,
        )
        return response.choices[0].message.content
    def azure(self, p : PROMPT) -> str:
        client = ClientPipeline(provider=self.provider, model=self.model)()
        response = client.chat.completions.create(
                model=self.model,
                messages=p.messages,
                max_completion_tokens=self.max_tokens,
            )
        return response.choices[0].message.content