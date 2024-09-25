import os
import dotenv
from typing import Annotated, List, Optional, Union
from custom_types.PROMPT.type import PROMPT
import openai
from utils.booleans import to_bool
from pipelines.CONVERSIONS.txt_2_dict import Pipeline as TXT2DICT
import json

dotenv.load_dotenv()

class Pipeline:
    __env__ = ["openai_api_key"]

    def __init__(self, 
                 schema : str,
                 model : str = "gpt-4o-2024-08-06", 
                 base_url : str = "https://api.openai.com/v1",
                 temperature : int =1, 
                 retries : int =3, 
                 max_tokens : int =3500, 
                 top_p : int =1, 
                 frequency_penalty : float =0, 
                 presence_penalty : float=0):
        if not schema:
            raise Exception("schema is missing")
        else:
            self.json_schema = json.loads(schema)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.retries = retries
        self.base_url = base_url
        
    def __call__(self, 
                 p : PROMPT
                 ) -> dict:
        
        for _ in range(self.retries -1):
            try:
                return self.retry__call__(p)
            except Exception as e:
                print(f"Problem {e}")
                pass
        return {}

    def retry__call__(self, 
                 p : PROMPT
                 ) -> dict:
        api_key = os.environ.get("openai_api_key")
        client = openai.OpenAI(api_key=api_key, base_url=self.base_url)
        messages = p.messages
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            response_format= {
                "type": "json_schema",
                "json_schema": self.json_schema
            }
        )
        res = response.choices[0].message.content
        return json.loads(res)