from utils.logger import log, result
import os
import openai
from utils.booleans import to_bool
from custom_types.PROMPT.type import PROMPT



class Pipeline:
    __env__ = ["openai_api_key"]

    def __init__(self, 
                 model : str = "gpt-4-1106-preview", 
                 base_url : str = "https://api.openai.com/v1",
                 json_format : bool = False,
                 temperature : int =0, 
                 max_tokens : int =3500, 
                 top_p : int =1, 
                 frequency_penalty : float =0, 
                 presence_penalty : float=0):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.json_format = to_bool(json_format) 
        self.base_url = base_url

    def __call__(self, 
                 p : PROMPT
                 ) -> str:
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
            response_format= {"type": "json_object"} if self.json_format else None
        )
        
        res = response.choices[0].message.content
        return res

