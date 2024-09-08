from typing import List, Dict, Any, Union
from pydantic import BaseModel, Field, create_model
import json
    
class ExclusionCriteria(BaseModel):
    name: str = Field(..., description = "The name of the exclusion criteria. Should be upper, no special characters, spaces replaced by underscores and no numbers.")
    exclusion_criteria: str = Field(..., description = "Describe precisely the situation where this exclusion criteria should be applied.")

class InclusionCriteria(BaseModel):
    name: str = Field(..., description = "The name of the selection criteria. Should be upper, no special characters, spaces replaced by underscores and no numbers.")
    inclusion_criteria: str = Field(..., description = "Describe precisely the situation where this inclusion criteria should be applied.")

class SELECT(BaseModel):
    selection_criteria : List[Union[ExclusionCriteria, InclusionCriteria]] = Field(..., description = "List of selection criteria") 
    
    def get_model(self):
        x = {}
        for e in self.selection_criteria:
            is_exclusion = type(e) == ExclusionCriteria
            x[e.name + '_JUSTIFICATION'] = (str, Field(..., description = f'Justifiy briefly the answer you want to give to {e.name} ({e.exclusion_criteria if is_exclusion else e.inclusion_criteria}). Be fair and unbiased. Your reflexion should aim at avoiding traps, making sure not to miss data, and avoid errors.'))
            x[e.name] = (bool, Field(..., description = e.exclusion_criteria if is_exclusion else e.inclusion_criteria))
        return create_model("Data", **x)
    
class Converter:
    @staticmethod
    def to_bytes(obj : SELECT) -> bytes:
        return bytes(obj.model_dump_json(), encoding = 'utf-8')
         
    @staticmethod
    def from_bytes(obj : bytes) -> 'SELECT':
        return SELECT.parse_obj(json.loads(obj.decode('utf-8')))
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='select',
    _class = SELECT,
    converter = Converter,
    additional_converters={
        'json':lambda x : x.to_dict()
        },
    icon='/micons/deepsource.svg'
)