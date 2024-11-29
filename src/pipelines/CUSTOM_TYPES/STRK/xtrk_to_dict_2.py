import os
from custom_types.PROMPT.type import PROMPT
from custom_types.XTRK.type import DataStructure, _create_model
import tiktoken 
import json
import openai

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self, 
                 reflexive_model : str = "o1-preview",
                 formatter_model : str = "gpt-4o",
                 max_tokens : int = 32000
                 ):
        self.reflexive_model = reflexive_model
        self.formatter_model = formatter_model
        self.max_tokens = max_tokens
        
    def __call__(self, 
                 text : str,
                 schema : DataStructure
                 ) -> dict:
        encoding              = tiktoken.encoding_for_model(self.reflexive_model)
        dumped_schema         = schema.model_dump_json(indent = 1)
        prompt                = f'Please extract data from the article above, as a json dictionary, using the schema description below.\n\n{dumped_schema}'
        n_text_tokens         = len(encoding.encode(text))
        n_prompt_tokens       = len(encoding.encode(prompt))
        n_allowed_text_tokens = self.max_tokens - n_prompt_tokens
        if n_allowed_text_tokens < 1000:
            raise ValueError(f"Text too long: {n_text_tokens} tokens. Maximum allowed text length: {n_allowed_text_tokens} tokens.")
        p = min(1, n_allowed_text_tokens/n_text_tokens*0.9)
        text = text[:int(len(text) * p)]
        client = openai.OpenAI(api_key=os.environ.get("openai_api_key"))
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
        formatted_response = formatted_response.choices[0].message.parsed.model_dump()
        return formatted_response