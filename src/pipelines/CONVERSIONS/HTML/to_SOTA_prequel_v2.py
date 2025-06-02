from custom_types.HTML.type import HTML
from custom_types.PROMPT.type import PROMPT
from bs4 import BeautifulSoup
from pipelines.LLMS.v3.client import Providers
from pipelines.LLMS.v3.str import Pipeline as LLM
from pipelines.CONVERSIONS.HTML.to_SOTA_prequel import parse_and_verify, default_prompt

class Pipeline:
    def __init__(self, 
                 model : str = "gpt-4.1",
                 provider: Providers = 'openai',
                 prompt : str = default_prompt):
        self.model = model
        self.prompt = prompt
        self.provider = provider

    def __call__(self, doc: dict) -> dict:
        prompt = PROMPT()
        prompt.add(doc['new_contracted_html'], role="user")
        prompt.add(self.prompt, role="system")
        pipeline = LLM(model = self.model, provider=self.provider)
        res = pipeline(prompt)
        doc['cleaned_html'] = parse_and_verify(res)
        return doc