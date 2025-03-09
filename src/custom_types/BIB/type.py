from typing import List, Literal
from dataclasses import dataclass
import json 

@dataclass
class BIB:
    title: str
    abstract : str
    doi : str
    date : str
    journal : str
    authors : List[str]
    type : List[str]
    keywords : List[str]
    affiliations : List[str]
    full_entry_type : Literal['PUBMED', 'OTHER']
    full_entry : dict
    
class Converter:
    @staticmethod
    def to_bytes(url : BIB) -> bytes:
        return bytes(json.dumps(url.__dict__), 'utf-8')
        
    @staticmethod
    def from_bytes(b: bytes) -> BIB:
        loaded_str = b.decode('utf-8')
        return BIB(**json.loads(loaded_str))
        
    @staticmethod
    def str_preview(url : BIB) -> str:
        return json.dumps(url.__dict__, indent = 1)
    
    @staticmethod
    def len(bib : BIB) -> int:
        return 1
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='bib',
    _class = BIB,
    converter = Converter,
    inputable  = False,
    hide=hasattr(Converter, 'hide') and callable(getattr(Converter, 'hide')),
    additional_converters={
        'json':lambda x : x.__dict__
        },
    icon='/icons/doc.svg'#'lib'
)