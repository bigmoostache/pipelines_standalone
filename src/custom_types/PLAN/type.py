from typing import BaseModel, List, Dict, Any
class POSSIBLE_VALUE(BaseModel):
    value : int
    definition : str

class NOTATION_CRITERIA(BaseModel):
    name : str
    definition : str
    possible_values : List[POSSIBLE_VALUE]

class GRID(BaseModel):
    rows: List[NOTATION_CRITERIA]
    
    def to_dict(self):
        return self.dict()
    def from_dict(self, d: Dict[str, Any]):
        return self.parse_obj(d)

from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='plan',
    _class = Plan,
    converter = Converter
)