import os
import dotenv
from typing import Annotated, List, Optional, Union
from custom_types.PROMPT.type import PROMPT
from openai import AzureOpenAI
from pipelines.CONVERSIONS.txt_2_dict import Pipeline as TXT2DICT
import json

class Pipeline:
    __env__ = ['AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT']

    def __init__(self, 
                 schema : str,
                 model : str = "gpt-4o-2024-08-06", 
                 temperature : int =1, 
                 retries : int =3, 
                 max_tokens : int =3500, 
                 top_p : int =1, 
                 frequency_penalty : float =0, 
                 presence_penalty : float=0):
        if not schema:
            raise Exception("schema is missing")
        else:
            self.json_schema = json.loads(schema)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.retries = retries

    def __call__(self, p: PROMPT) -> dict:
        p.truncate()
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-08-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        messages = p.messages
        attempts = 0

        while attempts < self.retries:
            try:
                completion = client.beta.chat.completions.parse(
                    model=self.model,
                    messages=messages,
                    temperature=1,
                    max_tokens=self.max_tokens,
                    top_p=self.top_p,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty,
                    response_format={
                        'type': 'json_schema',
                        'json_schema': {
                            'schema': self.json_schema,
                            'name': 'ResultStructure'
                        }
                    }
                )
                res = completion.choices[0].message.content
                return json.loads(res)

            except Exception as e:
                attempts += 1
                if attempts >= self.retries:
                    print(f"Maximum retries reached ({self.retries}). Returning empty dict.")
                    return {}
                else:
                    print(f"Error encountered ({type(e).__name__}). Retrying {attempts}/{self.retries}...")
                    # Optionally, adjust parameters to prevent the error in next attempt
                    # For example, reduce max_tokens or modify the prompt
                    continue  # Retry the API call

            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An unexpected error occurred: {e}")
                raise e
