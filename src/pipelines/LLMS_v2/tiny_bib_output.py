from custom_types.PROMPT.type import PROMPT
from custom_types.GRID.type import GRID
from custom_types.TINY_BIB.type import TINY_BIB
import openai
import logging 
import os
logging.basicConfig(level=logging.INFO)

class Pipeline:
    __env__ = ["openai_api_key"]

    def __init__(self, 
                 model : str = "gpt-4o-2024-08-06", 
                 base_url : str = "https://api.openai.com/v1",
                 temperature : int =1, 
                 retries : int =3, 
                 top_p : int =1):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.retries = retries
        self.base_url = base_url
        
    def __call__(self, 
                 p : PROMPT,
                 ) -> TINY_BIB:
        api_key = os.environ.get("openai_api_key")
        client = openai.OpenAI(api_key=api_key, base_url=self.base_url)
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
    