import os
from typing import List, Literal
from custom_types.SELECT.type import SELECT
from custom_types.PROMPT.type import PROMPT
from pipelines.LLMS.v3.client import Pipeline as ClientPipeline, Providers
import json
from custom_types.trees.gap_analysis.type import ResponseType as Tree_Gap_AnalysisResponseType
from custom_types.TINY_BIB.type import TINY_BIB
from custom_types.XTRK.type import DataStructure
from pipelines.MANIPS.XLSX.table_to_tables import Schema

output_formats = {
    'tree/gap_analysis': Tree_Gap_AnalysisResponseType,
    'select': SELECT,
    'tiny_bib': TINY_BIB,
    'xtrk': DataStructure,
    'simple_schema': Schema
}

class Pipeline:
    def __init__(self,
        provider: Providers = "openai",
        model: str = "gpt-4.1",
        hard_coded_model: Literal['none', 'tree/gap_analysis', 'select', 'tiny_bib', 'xtrk', 'simple_schema'] = 'none',
        convert_back_to_dict: bool = False,
        temperature: float = 0.5
        ):
        self.provider = provider
        self.model = model
        self.hard_coded_model = hard_coded_model
        self.convert_back_to_dict = convert_back_to_dict
        self.temperature = temperature
        
    def __call__(self, 
                p : PROMPT,
                output_format : str,
                mode: str = 'structured', #Literal['structured', 'json_schema']
                ) -> dict:
        if self.hard_coded_model != 'none':
            output_format = output_formats[self.hard_coded_model]
            mode = 'structured'
        # for now, str as output, but this will change
        if self.provider == "openai":
            response = self.openai(p, output_format, mode)
        elif self.provider == "azure":
            response = self.azure(p, output_format, mode)
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented")
        if self.convert_back_to_dict:
            response = response.model_dump()
        return response
    def openai(self, p : PROMPT, output_format: str, mode: str) -> str:
        client = ClientPipeline(provider=self.provider, model=self.model)()
        if mode == 'structured':
            response = client.beta.chat.completions.parse(
                model=self.model,
                messages=p.messages,
                response_format=output_format,
                temperature=self.temperature
            )
            return response.choices[0].message.parsed
        else:
            response = client.chat.completions.create(
                model=self.model,
                messages=p.messages,
                response_format={ 
                            'type': 'json_schema',
                            'json_schema': {
                                'schema': output_format,
                                'name': 'ResultStructure'
                            }
                } if 'json_schema' not in output_format else output_format,
                temperature=self.temperature
            )
            return json.loads(response.choices[0].message.content)
        
    def azure(self, p : PROMPT, output_format: str, mode: str) -> str:
        client = ClientPipeline(provider=self.provider, model=self.model)()
        if mode == 'structured':
            response = client.beta.chat.completions.parse(
                    model=self.model,
                    messages=p.messages,
                    response_format=output_format,
                    temperature=self.temperature
                )
            return response.choices[0].message.parsed
        else:
            response = client.chat.completions.create(
                model=self.model,
                messages=p.messages,
                response_format={
                    'type': 'json_schema',
                    'json_schema': {
                        'schema': output_format,
                        'name': 'ResultStructure'
                    }
                } if 'json_schema' not in output_format else output_format,
                temperature=self.temperature
            )
            return response.choices[0].message.content