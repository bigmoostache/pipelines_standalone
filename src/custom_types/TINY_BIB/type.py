from typing import List
import json 
from pydantic import BaseModel, Field
from typing import Optional

class TINY_BIB(BaseModel):
    title: str = Field(..., description = "Article title")
    reference: str = Field(..., description = "Article reference, APA format. As complete as possible.")
    doi : Optional[str] = Field(..., description = "Article doi")
    date : Optional[str] = Field(..., description = "Publication Date, ISO 8601 format: one of: YYYY-MM-DD, YYYY-MM, or YYYY, the most specific format available. Failing to comply with this format will result in an error.")
    journal : Optional[str] = Field(..., description = "Article journal")
    authors : List[str] = Field(..., description = "Article authors")
    context: str = Field(..., description = "Article context, a brief summary of the article: its objectives, methods, and results. Max 3 sentences.")
    
class Converter:
    @staticmethod
    def to_bytes(bib : TINY_BIB) -> bytes:
        return bytes(json.dumps(bib.dict()), 'utf-8')
        
    @staticmethod
    def from_bytes(b: bytes) -> TINY_BIB:
        return TINY_BIB.model_validate(json.loads(b.decode('utf-8')))
    
    @staticmethod
    def len(bib : TINY_BIB) -> int:
        return 1
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='tiny_bib',
    _class = TINY_BIB,
    converter = Converter,
    inputable  = False,
    additional_converters={
        'json':lambda x : x.dict()
        },
    icon='/micons/lib.svg'
)