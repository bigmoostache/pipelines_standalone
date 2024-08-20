from typing import List, Dict, Any
from pydantic import BaseModel
import json

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
    rows: List[GRID_SECTION]
    def to_dict(self):
        return self.dict()
 
    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        return cls.parse_obj(d)
    
class Converter:
    @staticmethod
    def to_bytes(obj : GRID) -> bytes:
        return bytes(json.dumps(obj.to_dict()), encoding = 'utf-8')
         
    @staticmethod
    def from_bytes(obj : bytes) -> 'GRID':
        return GRID.parse_obj(json.loads(obj.decode('utf-8')))
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='grid',
    _class = GRID,
    converter = Converter,
    additional_converters={
        'json':lambda x : x.to_dict()
        }
)