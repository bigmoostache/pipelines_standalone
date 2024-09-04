from typing import List, Literal, Optional
from dataclasses import dataclass, asdict
import json 

@dataclass
class AUTHOR:

    full_name: str
    affiliations: Optional[List[str]]
    h_index: Optional[int]


class Converter:
    @staticmethod
    def to_bytes(url : AUTHOR) -> bytes:
        return bytes(json.dumps(url.__dict__), 'utf-8')
        
    @staticmethod
    def from_bytes(b: bytes) -> AUTHOR:
        loaded_str = b.decode('utf-8')
        return AUTHOR(**json.loads(loaded_str))
        
    @staticmethod
    def str_preview(url : AUTHOR) -> str:
        return json.dumps(url.__dict__, indent = 1)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='author',
    _class = AUTHOR,
    converter = Converter,
    inputable  = False,
    additional_converters={
        'json':lambda x : x.__dict__
        },
    icon='Authors'
)