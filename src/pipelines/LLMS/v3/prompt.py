from typing import Literal
from custom_types.PROMPT.type import PROMPT
from pipelines.LLMS.v3.str import Pipeline as StrPipeline
from pipelines.LLMS.v3.client import Providers, ReasoningEffort

class Pipeline:
    def __init__(self,
        provider: Providers = "openai",
        model: str = "gpt-4.1",
        role: str = "user",
        reasoning_effort: ReasoningEffort = "none",
        ):
        self.provider = provider
        self.model = model
        self.role = role
        self.reasoning_effort = reasoning_effort
    def __call__(self, 
                p : PROMPT) -> PROMPT:
        pipeline = StrPipeline(provider=self.provider, model=self.model, reasoning_effort=self.reasoning_effort)
        str_output = pipeline(p)
        p.add(str_output, role =self.role)
        return p
