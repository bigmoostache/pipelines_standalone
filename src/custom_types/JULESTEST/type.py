from typing import List, Literal
from dataclasses import dataclass
import json 

@dataclass
class DAM_full_text_select: #avoir un tableau excel
    title_pdf: str
    title_article: str
    first_author : str
    journal : str
    full_entry : dict # donc il faut répondre au prompt comme DAM_select.  Include all articles regarding nail removal. => donc il faut un tableau TRUE/FALSE et explication
                      #  In those articles extract : reason of removal, iatrogenic complications of the removal, delay of removal, length of the nail, type of nail, rotator cuff state 
    
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
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='bib',
    _class = BIB,
    converter = Converter,
    inputable  = False,
    additional_converters={
        'json':lambda x : x.__dict__
        }
)