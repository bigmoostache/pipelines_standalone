from pydantic import BaseModel, Field, create_model
from typing import Literal, List, Any, Union, Optional
from datetime import datetime
from enum import Enum
import json
import requests

class FileTypes(str, Enum):
    txt = 'txt'
    pdf = 'pdf'
    png = 'png'
    jpg = 'jpg'
    jpeg = 'jpeg'
    webp = 'webp'
    word = 'docx'
    msword = 'doc'
    ppt = 'ppt'
    pptx = 'pptx'
    csv = 'csv'
    url = 'url'
    
    image_desc = 'image_desc'
    text_chunk = 'text_chunk'
    csv_desc = 'csv_desc'

class PipelineStatus(str, Enum):
    anticipated = 'anticipated'
    pending = 'pending'
    success = 'success'
    error = 'error'
    retrying = 'retrying'
    
class Document(BaseModel):
    file_id: int = Field(default=None, primary_key=True)
    parent_file_id : Optional[int]
    direct_parent_file_id : Optional[int]
    file_uuid : str
    file_name : str
    file_hash : str
    file_ext : FileTypes
    upload_date : str
    pipeline_status : PipelineStatus
    ext_project_id : str
    
    context : Optional[str] # To situate within the parent document, e.g. a paragraph number
    position : Optional[int] # To order within the parent document
    description : Optional[str] # For root documents: a description of the document

    # The two below are not expected to be files in the database.
    text : Optional[str] # For textualizable documents: the text content
    score : Optional[float] # For documents with scores, e.g. relevance
    raw_url : Optional[str] # Provided to the user for download

class LUCARIO(BaseModel):
    url: str = Field(..., description = 'The URL of lucario hosted service.')
    project_id: str = Field(..., description = 'The project id.')
    elements: List[Document] = Field(..., description = 'The elements to be analyzed.')
    uuid_2_position: Dict[str, int] = Field(..., description = 'The mapping of uuid to position.')
    file_id_2_position: Dict[int, int] = Field(..., description = 'The mapping of file_id to position.')
    
    def post_file(self, file_bytes: bytes, file_name: str) -> Document:
        response = requests.post(
            f'{self.url}/files', 
            params = {'project_id': self.project_id},
            headers = {'accept': 'application/json'}, 
            files = { 'file': (file_name, file_bytes, 'application/octet-stream') }
            )
        return Document.parse_obj(response.json())
    
    def add_document(self, document: Document):
        if document.file_id in self.file_id_2_position:
            self.elements[self.file_id_2_position[document.file_id]] = document
        elif document.file_uuid in self.uuid_2_position:
            self.elements[self.uuid_2_position[document.file_uuid]] = document
        else:
            self.elements.append(document)
            self.uuid_2_position[document.file_uuid] = len(self.elements) - 1
            self.file_id_2_position[document.file_id] = len(self.elements) - 1
            
    def anchored_top_k(self, queries: List[str], max_groups_per_element: int, elements_per_group: int, min_elements_per_list: int, file_uuids: List[str] = None) -> List[Document]:
        if file_uuids is None:
            file_uuids = [document.file_uuid for document in self.elements]
        else:
            # check if all file_uuids are in the elements
            for file_uuid in file_uuids:
                if file_uuid not in self.uuid_2_position:
                    raise ValueError(f'file_uuid {file_uuid} not in the elements')
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        json_data = {
            'project_id': self.project_id,
            'query_texts': queries,
            'max_groups_per_element': max_groups_per_element,
            'elements_per_group': elements_per_group,
            'min_elements_per_list': min_elements_per_list,
            'file_uuids': file_uuids
        }

        response = requests.post(f'{self.url}/anchored_top_k', headers=headers, json=json_data)
        return [Document.parse_obj(document) for document in response.json()]
    
    
class Converter:
    @staticmethod
    def to_bytes(obj : LUCARIO) -> bytes:
        return bytes(obj.model_dump_json(), encoding = 'utf-8')
         
    @staticmethod
    def from_bytes(obj : bytes) -> LUCARIO:
        return SELECT.parse_obj(json.loads(obj.decode('utf-8')))
    
    @staticmethod
    def len(obj : LUCARIO) -> int:
        return 1
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='lucario',
    _class = LUCARIO,
    converter = Converter,
    additional_converters={
        'json':lambda x : x.to_dict()
        },
    icon='/micons/deepsource.svg',
)