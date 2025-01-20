from custom_types.PROMPT.type import PROMPT
from custom_types.SELECT.type import SELECT
from openai import AzureOpenAI
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
        
    def __call__(self, 
                 p : PROMPT,
                 ) -> SELECT:
        p.truncate()
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-08-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        completion = client.beta.chat.completions.parse(
            model=self.model,
            messages=p.messages,
            temperature=self.temperature,
            top_p=self.top_p,
            response_format=SELECT,
        )
        event = completion.choices[0].message.parsed
        return event
    