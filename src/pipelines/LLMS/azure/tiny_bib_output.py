from custom_types.PROMPT.type import PROMPT
from custom_types.GRID.type import GRID
from custom_types.TINY_BIB.type import TINY_BIB
from openai import AzureOpenAI
import logging 
import os
logging.basicConfig(level=logging.INFO)

class Pipeline:
    __env__ = ['AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT']

    def __init__(self, 
                 model : str = "gpt-4o", 
                 temperature : int =1, 
                 retries : int =3, 
                 top_p : int =1):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.retries = retries
        
    def __call__(self, 
                 p : PROMPT,
                 ) -> TINY_BIB:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-08-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        completion = client.beta.chat.completions.parse(
            model=self.model,
            messages=p.messages,
            temperature=self.temperature,
            top_p=self.top_p,
            response_format=TINY_BIB,
        )

        event = completion.choices[0].message.parsed
        if not isinstance(event, TINY_BIB):
            raise Exception("Invalid response")
        return event
    