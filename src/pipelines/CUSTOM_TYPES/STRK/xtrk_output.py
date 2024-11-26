import os, openai
from custom_types.PROMPT.type import PROMPT
from custom_types.XTRK.type import DataStructure

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self, 
                 model : str = "gpt-4o-2024-08-06"):
        self.model = model
    def __call__(self, 
                 p : PROMPT
                 ) -> DataStructure:
        return openai.OpenAI(
            api_key=os.environ.get("openai_api_key")
            ).beta.chat.completions.parse(
                    model=self.model,
                    messages=p.messages,
                    response_format=DataStructure
            ).choices[0].message.parsed