from typing import List, Literal, Optional
from dataclasses import dataclass, asdict
from custom_types.AUTHOR.type import AUTHOR
import json 

@dataclass
class RA:

    title: str
    abstract: str
    doi: str
    publication_date: str  # format yyyy-mm-dd or yyyy-mm or yyyy
    journal: str

    # Implement Type later
    authors: List[AUTHOR] 

    country: Optional[str]  # main country if the authors (based on affiliation) alpha-2 code
    data: Optional[Literal[
        "Clinical", "Epidemiological", "Litterature", "Genetic/Biomolecular", "Survey"
    ]]
    type: Optional[Literal[
        "Clinical Trial",
        "Review",
        "Case Report",
        "Meta-Analysis",
        "Erratum",
        "Retrospective Study",
        "Prospective Study",
        "Longitudinal Study",
        "Other",
    ]]
    keywords: Optional[List[str]] # tags ?
    method: Optional[str]
    full_entry_type: Optional[Literal["CROSSREF", "PUBMED", "OTHER"]]
    full_entry: Optional[dict]


    # TODO: Implement TYPE later
    theme_analyzis: Optional[str]
    # TODO; Implement TYPE later
    topics_analyzis: Optional[str]

    references: Optional[List[str]] # liste de doi
    citations: Optional[List[str]] # liste de doi
    pr: Optional[int] # pagerank calculated in a set of articles with references and citations
    is_new: Optional[bool] # if an article was in the original set of articles
    has_pdf:Optional[bool]  # if we have downloaded the pdf
    
class Converter:
    @staticmethod
    def to_bytes(url : RA) -> bytes:
        return bytes(json.dumps(url.__dict__), 'utf-8')
        
    @staticmethod
    def from_bytes(b: bytes) -> RA:
        loaded_str = b.decode('utf-8')
        return RA(**json.loads(loaded_str))
        
    @staticmethod
    def str_preview(url : RA) -> str:
        return json.dumps(url.__dict__, indent = 1)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='ra',
    _class = RA,
    converter = Converter,
    inputable  = False,
    additional_converters={
        'json':lambda x : x.__dict__
        },
    icon='micons/codeowners.svg'
)