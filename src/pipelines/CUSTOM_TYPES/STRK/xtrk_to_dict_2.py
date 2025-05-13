import os
from custom_types.PROMPT.type import PROMPT
from custom_types.XTRK.type import DataStructure, _create_model
import tiktoken 
import json
import openai
from pipelines.LLMS.v3.client import Providers
from pipelines.LLMS.v3.structured import Pipeline as StructuredPipeline
from pipelines.LLMS.v3.str import Pipeline as StrPipeline

def removenulls(d):
    if isinstance(d, dict):
        return {k: removenulls(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [removenulls(i) for i in d]
    else:
        return d
    
class Pipeline:
    def __init__(self, 
                 provider: Providers = "openai",
                 reflexive_model : str = "o1-preview",
                 formatter_model : str = "gpt-4o",
                 max_tokens : int = 32000,
                 simpler_model_if_no_list : bool = True
                 ):
        self.provider = provider
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
        p = PROMPT()
        p.add(text, 'user')
        p.add(prompt, 'user')
        return StructuredPipeline(
            provider=self.provider, 
            model=self.formatter_model,
            convert_back_to_dict=True,
        )(p, _create_model('ExtractedData', schema))
        
    def complicated_call(self, 
                 text : str,
                 schema : DataStructure
                 ) -> dict:
        try:
            encoding              = tiktoken.encoding_for_model(self.reflexive_model if 'o3' not in self.reflexive_model else 'o1-mini')
        except KeyError:
            encoding              = tiktoken.encoding_for_model('gpt-4o')
        dumped_schema         = schema.model_dump()
        dumped_schema         = json.dumps(removenulls(dumped_schema), indent = 2)
        prompt                = f'Please extract data from the article above, as a json dictionary, using the schema description below.\n\n{dumped_schema}\n\n- If you miss information, consequences will be absolutely catastrophic.\n- If you make mistakes, consequences will be absolutely catastrophic.\n-> You should be both super precise (NO MISTAKES) AND have a very very high recall (NO MISSING INFO). You are in competition with other models, so be as good as possible.'
        n_text_tokens, n_prompt_tokens         = len(encoding.encode(text)), len(encoding.encode(prompt))
        n_allowed_text_tokens = self.max_tokens - n_prompt_tokens
        if n_allowed_text_tokens < 1000:
            raise ValueError(f"Text too long: {n_text_tokens} tokens. Maximum allowed text length: {n_allowed_text_tokens} tokens.")
        p = min(1, n_allowed_text_tokens/n_text_tokens*0.9)
        text = text[:int(len(text) * p)]
        p = PROMPT()
        p.add(text, 'user')
        p.add(prompt, 'user')
        reflexive_response = StrPipeline(
            provider=self.provider, 
            model=self.reflexive_model
        )(p)
        p = PROMPT()
        p.add("Fit the provided json in the provided data strucure, VERBATIM.", 'system')
        p.add(reflexive_response, 'user')
        return StructuredPipeline(
            provider=self.provider, 
            model=self.formatter_model,
            convert_back_to_dict=True,
        )(p, _create_model('ExtractedData', schema))
    
    def __call__(self, 
                 text : str,
                 schema : DataStructure
                 ) -> dict:
        if self.simpler_model_if_no_list and not schema.at_least_one_field_is_a_data_structure():
            return self.simple_call(text, schema)
        return self.complicated_call(text, schema)