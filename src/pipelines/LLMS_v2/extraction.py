from custom_types.PROMPT.type import PROMPT
from custom_types.EXTRACTION.type import Entries
import openai
from typing import List
import os 

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self, 
                 model : str = "gpt-4o", 
                 base_url : str = "https://api.openai.com/v1",
                 temperature : float =1, 
                 top_p : float =1
                 ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.base_url = base_url
        
    def try_call(self, 
                 p : PROMPT,
                 e : Entries
                 ):
        client = openai.OpenAI(
            api_key=os.environ.get("openai_api_key"), 
            base_url=self.base_url)
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
        p.truncate()
        for k in range(3):
            success, result = self.try_call(p, e)
            if success:
                return result
        raise Exception("Failed to extract the event after 3 attempts")
    