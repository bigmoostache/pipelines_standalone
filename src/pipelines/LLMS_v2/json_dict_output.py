import os
import dotenv
from typing import Annotated, List, Optional, Union
from custom_types.PROMPT.type import PROMPT
import openai
from pipelines.CONVERSIONS.txt_2_dict import Pipeline as TXT2DICT
import json

dotenv.load_dotenv()

class Pipeline:
    __env__ = ["openai_api_key"]

    def __init__(self, 
                 schema : str,
                 model : str = "gpt-4o-2024-08-06", 
                 base_url : str = "https://api.openai.com/v1",
                 temperature : int =1, 
                 retries : int =3, 
                 max_tokens : int =3500, 
                 top_p : int =1, 
                 frequency_penalty : float =0, 
                 presence_penalty : float=0,
                 reasoning_effort : str = "high"
                 ):
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
        self.base_url = base_url
        self.reasoning_effort = reasoning_effort

    def __call__(self, p: PROMPT) -> dict:
        p.truncate()
        import json  # Ensure json is imported
        api_key = os.environ.get("openai_api_key")
        client = openai.OpenAI(api_key=api_key, base_url=self.base_url)
        messages = p.messages
        attempts = 0

        while attempts < self.retries:
            try:
                if 'o3' in self.model:
                    completion = client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        response_format={ 
                            'type': 'json_schema',
                            'json_schema': {
                                'schema': self.json_schema,
                                'name': 'ResultStructure'
                            }
                        } if 'json_schema' not in self.json_schema else self.json_schema,
                        reasoning_effort=self.reasoning_effort
                    )
                else:
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
                        } if 'json_schema' not in self.json_schema else self.json_schema
                    )
                res = completion.choices[0].message.content
                return json.loads(res)

            except Exception as e:
                attempts += 1
                if attempts >= self.retries:
                    raise e
                else:
                    print(f"Error encountered ({type(e).__name__}). Retrying {attempts}/{self.retries}... Details: {e}")
                    # Optionally, adjust parameters to prevent the error in next attempt
                    # For example, reduce max_tokens or modify the prompt
                    continue  # Retry the API call

            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An unexpected error occurred: {e}")
                raise e
