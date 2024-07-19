import os
import dotenv
from typing import Annotated, List, Optional, Union
import openai
from utils.booleans import to_bool

dotenv.load_dotenv()

class Pipeline:
    __env__ = ["openai_api_key"]

    def __init__(self, 
                 role_message : str, 
                 model : str = "gpt-4-1106-preview", 
                 json_format : bool = False,
                 temperature : int =0, 
                 max_tokens : int =3500, 
                 top_p : int =1, 
                 frequency_penalty : float =0, 
                 presence_penalty : float=0):
        self.model = model
        self.role_message = role_message
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.json_format = to_bool(json_format) 

    def __call__(self, 
                 user_message : str
                 ) -> str:
        """
        Execute the ChatGPT logic on the provided data.
        
        :param user_message: Message from the user to be processed by the model.
        :return: Response from the model.
        """
        api_key = os.environ.get("openai_api_key")
        # This code is for v1 of the openai package: pypi.org/project/openai
        client = openai.OpenAI(api_key=api_key)
        messages = [
                    {
                        "role": "user",
                        "content": user_message
                    },
                    {
                        "role": "user",
                        "content": self.role_message
                    }
                ]

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

