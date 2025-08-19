from pydantic import BaseModel, Field, create_model
from typing import Literal, List, Any, Union, Optional
import random, json

class Pubmed(BaseModel):
    pubmed_query: str = Field(..., description="Pubmed Query")
    pubmed_sort_by: Optional[Literal['best_match', 'most_recent', 'publication_date', 'first_author', 'journal']] = Field(None, description="Sort by field")
    pubmed_api_key: Optional[str] = Field(None, description="Pubmed API Key")
    pubmed_datetype: Optional[Literal['pdat', 'edat', 'mdat']] = Field(None, description="Date type for sorting")
    pubmed_reldate: Optional[int] = Field(None, description="Relative date for sorting")
    pubmed_mindate: Optional[str] = Field(None, description="Minimum date for sorting")
    pubmed_maxdate: Optional[str] = Field(None, description="Maximum date for sorting")
    