from pydantic import BaseModel, Field, create_model
from typing import Literal, List, Any, Union, Optional, Dict
from datetime import datetime
from enum import Enum
import json
import requests
from uuid import uuid4

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
    file_id: int # Useless in our context. ID of the file in the database
    parent_file_id : Optional[int]
    direct_parent_file_id : Optional[int]
    file_uuid : str # Also a unique ID, to be used in the LUCARIO object
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

    @classmethod
    def get_empty(cls) -> 'Document':
        return cls(
            file_id = -1,
            parent_file_id = None,
            direct_parent_file_id = None,
            file_uuid = '',
            file_name = '',
            file_hash = '',
            file_ext = FileTypes.txt,
            upload_date = '',
            pipeline_status = PipelineStatus.anticipated,
            ext_project_id = '',
            context = None,
            position = None,
            description = None,
            text = None,
            score = None,
            raw_url = None,
        )

class ForceChunk(BaseModel):
    file_uuid : str
    group_id : str
    chunk_id : Optional[int] = None  
    
class LUCARIO(BaseModel):
    url: str = Field('https://lucario.croquo.com', description = 'The URL of lucario hosted service.')
    project_id: str = Field(..., description = 'The project id.')
    elements: Dict[int, Document] = Field({}, description = 'local_id -> Document')
    uuid_2_position: Dict[str, int] = Field({}, description = 'uuid -> local_id')
    
    def post_file(self, file_bytes: bytes, file_name: str) -> Document:
        response = requests.post(
            f'{self.url}/files', 
            params = {'project_id': self.project_id},
            headers = {'accept': 'application/json'}, 
            files = { 'file': (file_name, file_bytes, 'application/octet-stream') }
            )
        return Document.parse_obj(response.json())
    def update(self):
        headers = {
            'accept': 'application/json',
        }
        params = {
            'project_id': self.project_id,
            'file_ids': ','.join([v.file_uuid for v in self.elements.values()]),
        }
        response = requests.get('https://lucario.croquo.com/files_simple', params=params, headers=headers)
        response = [Document.parse_obj(_) for _ in response.json()]
        for document in response:
            self.add_document(document)
        
    def add_document(self, document: Document):
        if document.file_uuid in self.uuid_2_position:
            self.elements[self.uuid_2_position[document.file_uuid]] = document
        else:
            self.elements[len(self.elements)] = document
            self.uuid_2_position[document.file_uuid] = len(self.elements) - 1
            
    def anchored_top_k(self, 
                       queries: List[str], 
                       group_ids: List[int], 
                       max_groups_per_element: int, 
                       elements_per_group: int, 
                       min_elements_per_list: int, 
                       file_uuids: List[str] = None,
                       files_forced:  List[ForceChunk] = []
                       ) -> List[Document]:
        if file_uuids is None:
            file_uuids = [document.file_uuid for document in self.elements.values()]
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
            'group_ids': group_ids,
            'max_groups_per_element': max_groups_per_element,
            'elements_per_group': elements_per_group,
            'min_elements_per_list': min_elements_per_list,
            'file_uuids': file_uuids,
            'files_forced': [_.dict() for _ in files_forced]
        }
        res = requests.post(
            f'{self.url}/anchored_top_k', 
            headers=headers, 
            json=json_data,
            timeout=99999999  # using a very high timeout value
            )
        print(res)
        return res.json()
    @classmethod
    def get_new(cls, url = 'https://lucario.croquo.com'):
        return cls(url = url, project_id = str(uuid4()))
    
    
class Converter:
    @staticmethod
    def to_bytes(obj : LUCARIO) -> bytes:
        return bytes(obj.model_dump_json(), encoding = 'utf-8')
         
    @staticmethod
    def from_bytes(obj : bytes) -> LUCARIO:
        return LUCARIO.parse_obj(json.loads(obj.decode('utf-8')))
    
    @staticmethod
    def len(obj : LUCARIO) -> int:
        return 1
   
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='lucario',
    _class = LUCARIO,
    converter = Converter,
    additional_converters={
        'json':lambda x : x.model_dump()
        },
    visualiser = "https://vis.deepdocs.net/lucario",
    icon='/micons/deepsource.svg',
)