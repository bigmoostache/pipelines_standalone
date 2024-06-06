from typing import List, Literal, Optional
from dataclasses import dataclass, asdict
import json
from datetime import datetime

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
    def to_dict(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, "__dataclass_fields__"):
            return {k: Converter.to_dict(v) for k, v in asdict(obj).items()}
        elif isinstance(obj, (list, tuple)):
            return [Converter.to_dict(i) for i in obj]
        return obj
    
    @staticmethod
    def to_bytes(report: FullReport) -> bytes:
        return bytes(json.dumps(Converter.to_dict(report)), 'utf-8')
    
    @staticmethod
    def from_dict(data, cls):
        if isinstance(data, dict):
            fieldtypes = {f.name: f.type for f in cls.__dataclass_fields__.values()}
            return cls(**{f: Converter.from_dict(data[f], fieldtypes[f]) for f in data})
        elif isinstance(data, list):
            elem_type = cls.__args__[0]
            return [Converter.from_dict(i, elem_type) for i in data]
        elif isinstance(data, str):
            try:
                return datetime.fromisoformat(data)
            except ValueError:
                return data
        else:
            return data
    
    @staticmethod
    def from_bytes(b: bytes) -> FullReport:
        data = json.loads(b.decode('utf-8'))
        return Converter.from_dict(data, FullReport)
    
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