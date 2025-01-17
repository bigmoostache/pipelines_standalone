import os
from custom_types.PROMPT.type import PROMPT
from custom_types.XTRK.type import DataStructure
from openai import AzureOpenAI

class Pipeline:
    __env__ = ['AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT']
    def __init__(self, 
                 model : str = "gpt-4o-2024-08-06"):
        self.model = model
    def __call__(self, 
                 p : PROMPT
                 ) -> DataStructure:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-07-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        return client.beta.chat.completions.parse(
                    model=self.model,
                    messages=p.messages,
                    response_format=DataStructure
            ).choices[0].message.parsed