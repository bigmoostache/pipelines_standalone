from custom_types.PROMPT.type import PROMPT
from custom_types.SELECT.type import SELECT
import os 

class Pipeline:
    __env__ = ['AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT']
    def __init__(self, 
                 model : str = "gpt-4o", 
                 rerolls: int = 1,
                 ):
        self.model = model
        self.rerolls = rerolls
        
    def __call__(self, 
             p : PROMPT,
             e : SELECT
             ) -> dict:
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        return e(p.messages, openai_api_key=api_key, model=self.model, rerolls=self.rerolls, use_azure=True, azure_endpoint=azure_endpoint)