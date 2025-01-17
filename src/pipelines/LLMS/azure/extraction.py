from custom_types.PROMPT.type import PROMPT
from custom_types.EXTRACTION.type import Entries
from openai import AzureOpenAI
from typing import List
import os 

class Pipeline:
    __env__ = ['AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT']
    def __init__(self, 
                 model : str = "gpt-4o", 
                 temperature : float =1, 
                 top_p : float =1
                 ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        
    def try_call(self, 
                 p : PROMPT,
                 e : Entries
                 ):
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-08-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        _type = e.get_nested_model()
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=p.messages,
            temperature=self.temperature,
            top_p=self.top_p,
            response_format=_type
        )
        event = completion.choices[0].message.parsed
        if not isinstance(event, _type):
            return False, None
        return True, e.get_result_dict(event, keep_justifications= True)
    
    def __call__(self, 
             p : PROMPT,
             e : Entries
             ) -> List[dict]:
        for k in range(3):
            success, result = self.try_call(p, e)
            if success:
                return result
        raise Exception("Failed to extract the event after 3 attempts")
    