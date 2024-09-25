from custom_types.URL.type import URL
import openai
import os
from pydantic import BaseModel, Field
from typing import List, Optional
from urllib.parse import urlparse

#function to get base domain name

class Pipeline:
    __env__ = ["openai_api_key"]

    def __init__(self, 
                 model : str = "gpt-4o-2024-08-06", 
                 base_url : str = "https://api.openai.com/v1",
                 temperature : int =1, 
                 retries : int =3, 
                 top_p : int =1):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.retries = retries
        self.base_url = base_url
        
    def __call__(self, 
                 url : URL,
                 ) -> URL:
        api_key = os.environ.get("openai_api_key")
        client = openai.OpenAI(api_key=api_key)
        class Response(BaseModel):
            original_text : str = Field(..., title="The original text, verbatim, but cleaned up (remove ads, menus, etc.)")
            telegraphic_text : str = Field(..., title="Translate the text above to telegraphic, non-verbal, prepositions-free, ultra-synthetic speech. Exactly the same content: if you change or forget information, you will be heavily penalized.")
        completion = client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": f"Process the text and images."},
                {"role": "user", "content": f'Source: {url.base_name}\nFull url: {url.url}\nTitle: {url.title}\nContents:\n{url.text}'}
            ],
            response_format=Response,
        )
        url.text = completion.telegraphic_text
        return url
    