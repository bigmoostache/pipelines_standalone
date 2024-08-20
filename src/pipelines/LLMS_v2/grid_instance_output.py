from custom_types.PROMPT.type import PROMPT
from custom_types.GRID.type import GRID
import openai
from utils.booleans import to_bool
from pipelines.CONVERSIONS.txt_2_dict import Pipeline as TXT2DICT
import logging 
import os
logging.basicConfig(level=logging.INFO)

class Pipeline:
    __env__ = ["openai_api_key"]

    def __init__(self, 
                 model : str = "gpt-4o", 
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
                 ) -> GRID:
        api_key = os.environ.get("openai_api_key")
        client = openai.OpenAI(api_key=api_key, base_url=self.base_url)
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=p.messages,
            temperature=self.temperature,
            top_p=self.top_p,
            response_format=GRID,
        )

        event = completion.choices[0].message.parsed
        if not isinstance(event, GRID):
            raise Exception("Invalid response")
        return event
    