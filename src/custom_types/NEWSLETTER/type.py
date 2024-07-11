from typing import List, Literal, Optional
from dataclasses import dataclass, asdict
import json, typing, base64
from datetime import datetime

class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return '___ASCII___' + base64.b64encode(obj).decode('ascii')  # convert bytes to base64 string
        return json.JSONEncoder.default(self, obj)

def bytes_decoder(dct):
    for key, value in dct.items():
        if isinstance(value, str) and value.startswith('___ASCII___'):
            try:
                # Attempt to decode the string as base64; revert if it fails
                value= value[11:]
                possible_bytes = base64.b64decode(value, validate=True)
                dct[key] = possible_bytes
            except (ValueError, base64.binascii.Error):
                continue
    return dct        
@dataclass
class SummaryEntry:
    title         : str
    analysis      : str
    reference_id  : str

@dataclass
class SummaryParagraph:
    title   : str
    entries : List[SummaryEntry]

@dataclass
class Article:
    reference_id     : str
    title            : str
    pertinence_score : int # over 10
    analysis         : List[str]
    summary          : str # short
    complete_entry   : str
    tags             : List[str]
    localization     : Literal["North America", "South America", "Europe", "Asia", "Africa", "World"]
    source           : str # Source of the article
    author           : Optional[str] # Author of the article
    sentiment        : Optional[Literal["positive", "negative", "neutral"]] # Sentiment analysis
    url              : Optional[str] # URL of the article
    image            : Optional[bytes] # Image of the article

@dataclass
class Metric:
    metric : str
    value  : float
    unit   : str   # max 10 characters
    previous_value : Optional[float]
    previous_relative_time : Optional[str] # describe the change

@dataclass
class NEWSLETTER:
    summary           : List[SummaryParagraph]
    articles          : List[Article]
    metrics           : List[Metric]
    timestamp         : str # When the report was generated
    summary_analysis  : str # Key takeaways of the report

class Converter:
    @staticmethod
    def to_bytes(full_report : NEWSLETTER) -> bytes:
        return bytes(json.dumps(asdict(full_report), cls=BytesEncoder), 'utf-8')
    
    @staticmethod
    def from_bytes(b: bytes) -> NEWSLETTER:
        loaded_str = b.decode('utf-8')
        return NEWSLETTER(**json.loads(loaded_str, object_hook=bytes_decoder))

    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='newsletter',
    _class = NEWSLETTER,
    converter = Converter,
    inputable  = False,
    visualiser = "https://visuals.croquo.com/newsletter"
)
