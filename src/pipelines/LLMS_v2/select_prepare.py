from custom_types.PROMPT.type import PROMPT
from custom_types.EXTRACTION.type import Entries
import openai
import os 

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self, 
                 model : str = "gpt-4o-2024-08-06", 
                 base_url : str = "https://api.openai.com/v1",
                 temperature : float =1, 
                 top_p : float =1
                 ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.base_url = base_url
        
    def __call__(self, 
                 p : PROMPT,
                 ) -> Entries:
        p.truncate()
        client = openai.OpenAI(
            api_key=os.environ.get("openai_api_key"), 
            base_url=self.base_url)
        completion = client.beta.chat.completions.parse(
            model=self.model,
            messages=p.messages,
            temperature=self.temperature,
            top_p=self.top_p,
            response_format=Entries,
        )
        event = completion.choices[0].message.parsed
        return event
    