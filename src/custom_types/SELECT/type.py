from typing import List, Dict, Any, Union
from pydantic import BaseModel, Field, create_model
import json
    
class ExclusionCriteria(BaseModel):
    exclusion_criteria_description: str = Field(..., description = "Describe precisely the situation where this exclusion criteria should be applied.")
    name: str = Field(..., description = "The name of the exclusion criteria. Should be upper, no special characters, spaces replaced by underscores and no numbers.")

class InclusionCriteria(BaseModel):
    inclusion_criteria_description: str = Field(..., description = "Describe precisely the situation where this inclusion criteria should be applied.")
    name: str = Field(..., description = "The name of the selection criteria. Should be upper, no special characters, spaces replaced by underscores and no numbers.")

class SELECT(BaseModel):
    selection_criteria : List[Union[ExclusionCriteria, InclusionCriteria]] = Field(..., description = "List of selection criteria") 
    
    def get_model(self):
        x = {}
        for e in self.selection_criteria:
            is_exclusion = type(e) == ExclusionCriteria
            x[e.name + '_JUSTIFICATION'] = (str, Field(..., description = f'Justifiy briefly the answer you want to give to {e.name} ({e.exclusion_criteria_description if is_exclusion else e.inclusion_criteria_description}). Be fair and unbiased. Your reflexion should aim at avoiding traps, making sure not to miss data, and avoid errors.'))
            x[e.name] = (bool, Field(..., description = e.exclusion_criteria_description if is_exclusion else e.inclusion_criteria_description))
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