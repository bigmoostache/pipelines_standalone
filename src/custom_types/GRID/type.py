from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, create_model
import json, re

class POSSIBLE_VALUE(BaseModel):
    value: int
    definition: str

class NOTATION_CRITERIA(BaseModel):
    name: str
    definition: str
    possible_values: List[POSSIBLE_VALUE]

class GRID_SECTION(BaseModel):
    name : str
    rows: List[NOTATION_CRITERIA]
    
class GRID(BaseModel):
    context: Optional[str] = Field('', title="Context", description="Additional information about the grid")
    rows: List[GRID_SECTION]
    def to_dict(self):
        return self.dict()
 
    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        return cls.parse_obj(d)
    
    def create_model(self, name: str = 'GRID') -> type:
        x = {}
        for section in self.rows:
            for row in section.rows:
                root_name = re.sub(r'[^a-zA-Z0-9 -]', '', row.name)
                root_name = re.sub(r'[ -]', '_', root_name)
                root_name = re.sub(r'_+', '_', root_name).strip('_')
                y = {
                    f'{root_name}_analysis': (str, Field(..., description=f'Analysis for the {row.name} section.')),
                    f'{root_name}_value': (int, Field(..., description=f'Value for the {row.name} section.')),
                }
                x[root_name] = (create_model(f'{row.name}_Model', **y), Field(..., description=f'{row.definition}, with possible values: {row.possible_values}'))
        return create_model(name, **x)
    
class Converter:
    @staticmethod
    def to_bytes(obj : GRID) -> bytes:
        return bytes(json.dumps(obj.to_dict()), encoding = 'utf-8')
         
    @staticmethod
    def from_bytes(obj : bytes) -> 'GRID':
        return GRID.parse_obj(json.loads(obj.decode('utf-8')))
    
    @staticmethod
    def len(obj : GRID) -> int:
        return 1
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='grid',
    _class = GRID,
    converter = Converter,
    additional_converters={
        'json':lambda x : x.to_dict()
        },
    icon='/micons/deepsource.svg',
    visualiser = "https://vis.deepdocs.net/grid",
)
