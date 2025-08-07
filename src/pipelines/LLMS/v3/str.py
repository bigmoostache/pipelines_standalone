import os
from typing import List, Literal
from custom_types.PROMPT.type import PROMPT
from pipelines.LLMS.v3.client import Pipeline as ClientPipeline, Providers, ReasoningEffort

import re

def extract_code_block(text, block_label):
    text += '\n```' # in case the LLM forgot to close
    pattern = f"```{block_label}\n(.*?)\n```"
    matches = re.findall(pattern, text, re.DOTALL)
    if not matches:
        raise ValueError(f"No code block with label '{block_label}' found")
    if len(matches) > 1:
        raise ValueError(f"Multiple code blocks with label '{block_label}' found")
    return matches[0]

class Pipeline:
    def __init__(self,
        provider: Providers = "openai",
        model: str = "gpt-4.1",
        reasoning_effort: ReasoningEffort = "none",
        ):
        self.provider = provider
        self.model = model
        self.reasoning_effort = reasoning_effort
    def __call__(self, 
                p : PROMPT) -> str:
        # for now, str as output, but this will change
        if self.provider == "openai":
            return self.openai(p)
        elif self.provider == "azure":
            return self.azure(p)
        elif self.provider == "anthropic":
            return self.anthropic(p)
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented")
    def openai(self, p : PROMPT) -> str:
        client = ClientPipeline(provider=self.provider, model=self.model)()
        response = client.responses.create(
            model=self.model,
            input=[
                {
                    'role': m['role'], 
                    'content': m['content']
                } for m in p.messages
            ],
            text={
                "format": {
                "type": "text"
                }
            },
            reasoning={} if self.reasoning_effort == "none" else {'effort': self.reasoning_effort},
            tools=[],
            store=False
            )
        return response.output_text
    def azure(self, p : PROMPT) -> str:
        client = ClientPipeline(provider=self.provider, model=self.model)()
        response = client.chat.completions.create(
                model=self.model,
                messages=p.messages
            )
        return response.choices[0].message.content
    def anthropic(self, p : PROMPT) -> str:
        client = ClientPipeline(provider=self.provider, model=self.model)()
        max_tokens = 8192
        message  = client.messages.create(
                max_tokens=8192,
                model=self.model,
                messages=p.messages
            )
        return message.content