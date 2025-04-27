from pydantic import BaseModel
import json

class FACTORY(BaseModel):
    dictionary: dict
    
class Converter:
    @staticmethod
    def to_bytes(FACTORY) -> bytes:
        return bytes(json.dumps(FACTORY.dictionary, indent = 2), 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> MD:
        return FACTORY(dictionary=json.loads(b.decode('utf-8')))
    @staticmethod
    def len(f : FACTORY) -> int:
        return 1
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='factory',
    _class = FACTORY,
    converter = Converter,
    additional_converters={
        'json':lambda x : {'__text__':x.dictionary}
    }
)
