
from custom_types.SOTA.type import SOTA, pipelines, VersionedText, VersionedInformation
from custom_types.JSONL.type import JSONL
from typing import List 
import requests
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class Document(BaseModel):
    file_id: int
    parent_file_id : Optional[int]
    direct_parent_file_id : Optional[int]
    file_uuid : str
    file_name : str
    file_hash : str
    file_ext : str
    upload_date : datetime
    pipeline_status : str
    ext_project_id : str
    
    context : Optional[str] # To situate within the parent document, e.g. a paragraph number
    position : Optional[int] # To order within the parent document
    description : Optional[str] # For root documents: a description of the document
    
    # The two below are not expected to be files in the database.
    text : Optional[str] # For textualizable documents: the text content
    score : Optional[float] # For documents with scores, e.g. relevance
    raw_url : Optional[str] # Provided to the user for download
    parent_file_uuid : Optional[str]

def top_k_lucario() -> List[Document]:
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    json_data = {
        'project_id': '1728993524.7400432.9001c424-7692-435f-8592-e00abe3a51be',
        'query_text': 'Of the use of mathematics and computer science in the field of osteoporosis',
        'k': 10,
        'file_ids': [],
        'max_per_information': 0,
    }

    response = requests.post('https://lucario.croquo.com/top_k', headers=headers, json=json_data)
    return [Document(**_) for _ in response.json()]
   
def apply_top_k(sota : SOTA, information : VersionedInformation, versions_list : List[VersionedText]) -> SOTA:
    return sota
   
class Pipeline:
    def __init__(
        self,
        k : int = 10,
        max_per_information : int = 0,
        file_ids : List[int] = [],
        ):
        self.k = k
        self.max_per_information = max_per_information
        self.file_ids = file_ids

    def __call__(self, 
                 sota : SOTA
                 ) -> SOTA:
        versions_list = sota.versions_list(-1)
        mother = sota.information[sota.mother_id]
        active_ids = mother.get_all_children_ids(sota, sota.mother_id, versions_list)
        for k,information in sota.information.items():
            if (k not in active_ids) or (not information.exists_in_stack(versions_list)):
                continue
            sota = apply_top_k(sota, information, versions_list)
        return sota