import os
from openai import AzureOpenAI
from custom_types.PROMPT.type import PROMPT

class Pipeline:
    __env__ = ['AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT']

    def __init__(self, 
                 model : str = "gpt-4-1106-preview", 
                 output_role : str = "assistant",
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
        self.role = output_role

    def __call__(self, 
                 p : PROMPT
                 ) -> PROMPT:
        p.truncate()
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-08-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        messages = p.messages
        if 'o1' not in self.model:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
            )
        else:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
        res = response.choices[0].message.content
        p.add(res, role = self.role)
        return p

