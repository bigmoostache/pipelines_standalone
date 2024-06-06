from typing import List, Literal, Optional
from dataclasses import dataclass, asdict
import json
from datetime import datetime
from custom_types.JSON.type import BytesEncoder, bytes_decoder

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
class FullReport:
    summary           : List[SummaryParagraph]
    articles          : List[Article]
    metrics           : List[Metric]
    timestamp         : datetime # When the report was generated
    summary_analysis  : str # Key takeaways of the report

class Converter:
    @staticmethod
    def to_bytes(full_report : FullReport) -> bytes:
        return bytes(json.dumps(asdict(full_report), cls=BytesEncoder), 'utf-8')
    
    @staticmethod
    def from_bytes(b: bytes) -> FullReport:
        loaded_str = b.decode('utf-8')
        return FullReport(**json.loads(loaded_str, object_hook=bytes_decoder))
    
    @staticmethod
    def str_preview(report: FullReport) -> str:
        return json.dumps(Converter.to_dict(report), indent=2)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='newsletter',
    _class = FullReport,
    converter = Converter,
    inputable  = False
)