import os
import dotenv
import openai
from utils.booleans import to_bool
dotenv.load_dotenv()

class Pipeline:
    __env__ = ["openai_api_key"]

    def __init__(self, 
                 role_message : str = "You are a helpful assistant that answers questions concisely and accurately.", 
                 instructions : str = "Type here your Prompt with the instructions",
                 model : str = "gpt-4o", 
                 temperature : float=0, 
                 max_tokens : int=3500, 
                 json_format : bool=False,
                 top_p : int=0, 
                 frequency_penalty: float=0, 
                 presence_penalty : float=0):
        
        self.instructions = instructions
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.role_message = role_message
        self.json_format = to_bool(json_format)

    def __call__(self, 
                 user_message : str) -> str:
    
        api_key = os.environ.get("openai_api_key")
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
        model=self.model,
        messages=[
                {
                    "role": "system",
                    "content" : self.role_message
                },
                {
                    "role": "user",
                    "content" : self.instructions
                },
                {
                    "role": "user",
                    "content": user_message
                }

            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            response_format= {"type": "json_object"} if self.json_format else None
        )
        res = response.choices[0].message.content
        return res
