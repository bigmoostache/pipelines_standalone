import os
from custom_types.PROMPT.type import PROMPT
from openai import AzureOpenAI
from pipelines.CONVERSIONS.txt_2_dict import Pipeline as TXT2DICT

class Pipeline:
    __env__ = ['AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT']

    def __init__(self, 
                 verify : str,
                 model : str = "gpt-4-turbo", 
                 temperature : int = 1, 
                 retries : int =3, 
                 max_tokens : int =3500, 
                 top_p : int =1, 
                 frequency_penalty : float = 0, 
                 presence_penalty : float = 0):
        if not verify:
            self.verify = []
        else:
            self.verify = [x.strip() for x in verify.split(',')]
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.retries = retries
        
    def __call__(self, 
                 p : PROMPT
                 ) -> dict:
        p.truncate()
        for _ in range(self.retries -1):
            try:
                return self.retry__call__(p)
            except Exception as e:
                pass
        return {}

    def retry__call__(self, 
                 p : PROMPT
                 ) -> dict:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-08-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        messages = p.messages
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            response_format= {"type": "json_object"}
        )
        res = response.choices[0].message.content
        dic = TXT2DICT()(res)
        for k in self.verify:
            assert k in dic
        return dic