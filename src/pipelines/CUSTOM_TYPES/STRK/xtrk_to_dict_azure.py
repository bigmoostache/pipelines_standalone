import os
from custom_types.PROMPT.type import PROMPT
from custom_types.XTRK.type import DataStructure, _create_model
import tiktoken 
import json
from openai import AzureOpenAI

class Pipeline:
    __env__ = ['AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT']
    def __init__(self, 
                 reflexive_model : str = "o1-preview",
                 formatter_model : str = "gpt-4o",
                 max_tokens : int = 32000,
                 simpler_model_if_no_list : bool = True
                 ):
        self.reflexive_model = reflexive_model
        self.formatter_model = formatter_model
        self.max_tokens = max_tokens
        self.simpler_model_if_no_list = simpler_model_if_no_list
        
    def simple_call(self, 
                 text : str,
                 schema : DataStructure
                 ) -> dict:
        encoding              = tiktoken.encoding_for_model(self.reflexive_model)
        dumped_schema         = schema.model_dump_json(indent = 1)
        prompt                = f'Please extract data from the article above, using the schema description below.\n\n{dumped_schema}'
        n_text_tokens, n_prompt_tokens         = len(encoding.encode(text)), len(encoding.encode(prompt))
        n_allowed_text_tokens = self.max_tokens - n_prompt_tokens
        if n_allowed_text_tokens < 1000:
            raise ValueError(f"Text too long: {n_text_tokens} tokens. Maximum allowed text length: {n_allowed_text_tokens} tokens.")
        p = min(1, n_allowed_text_tokens/n_text_tokens*0.9)
        text = text[:int(len(text) * p)]
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-07-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        formatted_response = client.beta.chat.completions.parse(
            model=self.formatter_model,
            messages = [
                {"role": "user", "content": [{'type': 'text', 'text': text}]}, 
                {"role": "user", "content": [{'type': 'text', 'text': prompt}]}
            ],
            response_format=_create_model('ExtractedData', schema)
        )
        return formatted_response.choices[0].message.parsed.model_dump()
        
    def complicated_call(self, 
                 text : str,
                 schema : DataStructure
                 ) -> dict:
        encoding              = tiktoken.encoding_for_model(self.reflexive_model)
        dumped_schema         = schema.model_dump_json(indent = 1)
        prompt                = f'Please extract data from the article above, as a json dictionary, using the schema description below.\n\n{dumped_schema}'
        n_text_tokens, n_prompt_tokens         = len(encoding.encode(text)), len(encoding.encode(prompt))
        n_allowed_text_tokens = self.max_tokens - n_prompt_tokens
        if n_allowed_text_tokens < 1000:
            raise ValueError(f"Text too long: {n_text_tokens} tokens. Maximum allowed text length: {n_allowed_text_tokens} tokens.")
        p = min(1, n_allowed_text_tokens/n_text_tokens*0.9)
        text = text[:int(len(text) * p)]
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-07-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        reflexive_response = client.chat.completions.create(
            model = self.reflexive_model,
            messages = [
                {"role": "user", "content": [{'type': 'text', 'text': text}]}, 
                {"role": "user", "content": [{'type': 'text', 'text': prompt}]}
            ]
        )
        reflexive_response = reflexive_response.choices[0].message.content
        formatted_response = client.beta.chat.completions.parse(
            model=self.formatter_model,
            messages=[
                {"role": "system", "content": "Fit the provided json in the provided data strucure, VERBATIM."},
                {"role": "user", "content": reflexive_response},
            ],
            response_format=_create_model('ExtractedData', schema)
        )
        return formatted_response.choices[0].message.parsed.model_dump()
    
    def __call__(self, 
                 text : str,
                 schema : DataStructure
                 ) -> dict:
        if self.simpler_model_if_no_list and not schema.at_least_one_field_is_a_data_structure():
            return self.simple_call(text, schema)
        return self.complicated_call(text, schema)