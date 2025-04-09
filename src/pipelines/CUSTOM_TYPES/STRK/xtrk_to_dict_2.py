import os
from custom_types.PROMPT.type import PROMPT
from custom_types.XTRK.type import DataStructure, _create_model
import tiktoken 
import json
import openai

def removenulls(d):
    if isinstance(d, dict):
        return {k: removenulls(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [removenulls(i) for i in d]
    else:
        return d
    
class Pipeline:
    __env__ = ["openai_api_key"]
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
        dumped_schema         = schema.model_dump()
        # let's recursively remove all keys whose value is null
        dumped_schema         = json.dumps(removenulls(json.loads(dumped_schema)), indent = 2)
        prompt                = f'Please extract data from the article above, using the schema description below.\n\n{dumped_schema}'
        n_text_tokens, n_prompt_tokens         = len(encoding.encode(text)), len(encoding.encode(prompt))
        n_allowed_text_tokens = self.max_tokens - n_prompt_tokens
        if n_allowed_text_tokens < 1000:
            raise ValueError(f"Text too long: {n_text_tokens} tokens. Maximum allowed text length: {n_allowed_text_tokens} tokens.")
        p = min(1, n_allowed_text_tokens/n_text_tokens*0.9)
        text = text[:int(len(text) * p)]
        client = openai.OpenAI(api_key=os.environ.get("openai_api_key"))
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
        encoding              = tiktoken.encoding_for_model(self.reflexive_model if 'o3' not in self.reflexive_model else 'o1-mini')
        dumped_schema         = schema.model_dump()
        dumped_schema         = json.dumps(removenulls(dumped_schema), indent = 2)
        prompt                = f'Please extract data from the article above, as a json dictionary, using the schema description below.\n\n{dumped_schema}\n\n- If you miss information, consequences will be absolutely catastrophic.\n- If you make mistakes, consequences will be absolutely catastrophic.\n-> You should be both super precise (NO MISTAKES) AND have a very very high recall (NO MISSING INFO). You are in competition with other models, so be as good as possible.'
        open('X.txt', 'w').write(text + '\n\n\n' + prompt)
        n_text_tokens, n_prompt_tokens         = len(encoding.encode(text)), len(encoding.encode(prompt))
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
        open('Y.txt', 'w').write(text + '\n\n\n' + prompt + '\n\n\n' +reflexive_response)
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