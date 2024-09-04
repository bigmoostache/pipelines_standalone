import json
from typing import List
    
class URL:
    def __init__(self, 
                 url : str, 
                 title : str = "", 
                 images : List[str] = [], 
                 success: bool = False, 
                 text : str = "", 
                 clean_text : str = "", 
                 date : str = ""):
        self.url = url 
        self.title = title
        self.images = images
        self.success = success 
        self.text = text 
        self.clean_text = clean_text
        self.date = date
        
class Converter:
    extension = 'url'
    @staticmethod
    def to_bytes(url : URL) -> bytes:
        return bytes(json.dumps(url.__dict__), 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> URL:
        loaded_str = b.decode('utf-8')
        return URL(**json.loads(loaded_str))
    @staticmethod
    def str_preview(url : URL) -> str:
        return json.dumps(url.__dict__, indent = 1)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='url',
    _class = URL,
    converter = Converter,
    inputable  = False,
    additional_converters={
        'json':lambda x : x.__dict__
        },
    icon='/micons/url.svg'
)