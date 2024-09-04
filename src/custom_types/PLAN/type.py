import json
import base64
from dataclasses import dataclass, field, asdict, fields
from typing import List, Optional, Any, Dict
from custom_types.JSON.type import BytesEncoder, bytes_decoder
@dataclass
class Reference:
    source_id    : str
    start        : int
    end          : int
    comment      : str
    score        : int # sur 100
    user_frozen  : bool
    
@dataclass
class Source:
    id                  : str
    title               : str
    full_text           : str
    citation            : str
    figures             : List['Figure']
    penalization_factor : int

@dataclass
class Figure:
    title              : str
    comment            : str
    source_id          : str
    source_is_internal : bool                  # If internal, source_id should be the id of one of the sources
    contents           : Optional[bytes]
    user_feedback      : Optional[str]         # If set title and comment will be iterated. Context will be taken into account.


@dataclass
class Section:
    title                  : str
    title_feedback         : Optional[str] # If set, title will be iterated 

    abstract               : str
    abstract_feedback      : Optional[str] # If set, abstract will be iterated

    themes                 : List[str]
    themes_feedback        : Optional[str] # If set, themes will be iterated

    references             : List[Reference]
    references_feedback    : Optional[str] # If set, references will be recalculated

    redaction_directives   : Optional[str]
    full_text              : Optional[str]

    figures                : List[Figure]

    subsections_feedback   : str           # BE CAREFUL, IF SET, WILL OVERWRITE THE SUBSECTIONS WITH A NEW AI-GENERATED PROPOSITION
    subsections            : List['Section'] = field(default_factory=list)
    
@dataclass
class Plan:
    contents  : Section
    sources   : List[Source]

class Converter:
    @staticmethod
    def to_bytes(article : Plan) -> bytes:
        return bytes(json.dumps(asdict(article), cls=BytesEncoder), 'utf-8')

    @staticmethod
    def from_bytes(b: bytes) -> Plan:
        loaded_str = b.decode('utf-8')
        return Plan(**json.loads(loaded_str, object_hook=bytes_decoder))
    @staticmethod
    def str_preview(article : Plan) -> str:
        return json.dumps(asdict(article), cls=BytesEncoder, indent = 1)
    
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='plan',
    _class = Plan,
    converter = Converter,
    icon="roadmap"
)