from typing import Literal
import json
from custom_types.JSONL.type import JSONL
class PROMPT:
    def __init__(self):
        self.messages = []
    def add(self, message : str, 
            role : Literal["user", "system", "assistant"] = "user"):
        self.messages.append({"role" : role, "content" : message})
        
class Converter:
    extension = 'prompt'
    @staticmethod
    def to_bytes(p : PROMPT) -> bytes:
        _json = json.dumps(p.messages)
        return bytes(_json, 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> PROMPT:
        loaded_str = b.decode('utf-8')
        x =  json.loads(loaded_str)
        p = PROMPT()
        p.messages = x
        return p
    @staticmethod
    def str_preview(p: PROMPT) -> str:
        return json.dumps(p.messages, indent = 2)
    
    @staticmethod
    def len(p : PROMPT) -> int:
        # in K words
        return sum*([len(x['content'].split()) for x in p.messages]) // 1000
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='prompt',
    _class = PROMPT,
    converter = Converter,
    additional_converters={
        'jsonl':lambda x : JSONL(x.messages)
        },
    icon='/micons/coffee.svg'
)