from pydantic import BaseModel, Field, create_model
from typing import Literal, List, Any, Union, Optional, Dict
from datetime import datetime
from enum import Enum
from urllib.parse import quote
import json
import requests
from uuid import uuid4
from time import sleep, time
import os
from io import BytesIO
import httpx

class FileTypes(str, Enum):
    txt = "txt"
    pdf = "pdf"
    png = "png"
    jpg = "jpg"
    jpeg = "jpeg"
    webp = "webp"
    word = "word"
    msword = "msword"
    ppt = "ppt"
    pptx = "pptx"
    csv = "csv"
    url = "url"
    
    image_desc = "image_desc"
    text_chunk = "text_chunk"
    csv_desc = "csv_desc"
    
    vector_vendor = "vector_vendor"

class PipelineStatus(str, Enum):
    anticipated = 'anticipated'
    pending = 'pending'
    success = 'success'
    error = 'error'
    retrying = 'retrying'

class SubFile(BaseModel):
    raw_url: str
    pipeline_status: PipelineStatus
    file_ext: FileTypes
    local_chunk_identifier: int

class Document(BaseModel):
    file_id: int
    parent_file_id: int
    local_document_identifier: Optional[int] = None
    local_chunk_identifier: Optional[int] = None
    direct_parent_file_id: Optional[int] = None
    file_uuid: str
    file_name: str
    file_hash: str
    file_ext: FileTypes
    upload_date: str
    pipeline_status: PipelineStatus
    context: Optional[str] = None
    position: Optional[int] = None
    description: Optional[str] = None
    text: Optional[str] = None
    score: Optional[float] = None
    raw_url: Optional[str] = None

    subfiles: Optional[List[SubFile]] = []

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
    url: str = Field('https://lucario.deepdocs.net', description = 'The URL of lucario hosted service.')
    project_id: str = Field(..., description = 'The project id.')
    elements: Dict[int, Document] = Field({}, description = 'local_id -> Document')
    uuid_2_position: Dict[str, int] = Field({}, description = 'uuid -> local_id')
    file_id_2_position: Dict[int, int] = Field({}, description = 'file_id -> local_id')
    
    def post_file(self, file_bytes: bytes, file_name: str):
        file_bytes_stream = BytesIO(file_bytes)
        files = {'file': file_bytes_stream}
        encoded_filename = quote(file_name)
        headers = {'filename': encoded_filename, 'key': self.project_id}
        data = {'data': 'Uploaded from type.py - PIPELINES_STANDALONE'}

        with httpx.Client(timeout=60) as client:
            r = client.post(f'{self.url}/upload', data=data, files=files, headers=headers)
            if r.status_code != 200:
                raise ValueError(f'Error: {r.text}')
    
    def update(self):
        self.elements = {}
        self.uuid_2_position = {}
        self.file_id_2_position = {}
        headers = {
            'accept': 'application/json',
        }

        response = requests.get(
            f'{self.url}/projects/overview/{self.project_id}',
            headers=headers,
        )
        response = [Document.parse_obj(_) for _ in response.json()]
        for document in response:
            self.add_document(document)
            
    def wait_for_pendings(self, max_wait: int = 200):
        sleep(5)
        t0 = time()
        while True:
            self.update()
            if all([document.pipeline_status != PipelineStatus.pending for document in self.elements.values()]):
                break
            sleep(5)
            if time() - t0 > max_wait:
                raise ValueError('Timeout')
            
    def fetch_single(self, local_document_identifier, local_chunk_identifier) -> Document:
        response = requests.get(
            f'{self.url}/fetch_single',
            headers= {'accept': 'application/json'},
            params={
                'key': self.project_id,
                'document_identifier': local_document_identifier,
                'chunk_identifier': local_chunk_identifier,
            },
        )
        x = response.json()
        try:
            return Document.parse_obj(x)
        except Exception as e:
            raise ValueError(f'Error parsing document: {e}. Response: {x}') from e
        
    def add_document(self, document: Document):
        assert document.local_document_identifier is not None, 'local_document_identifier is None'
        self.elements[document.local_document_identifier] = document
        self.uuid_2_position[document.file_uuid] = document.local_document_identifier
        self.file_id_2_position[document.file_id] = document.local_document_identifier
        
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
            'key': self.project_id,
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
            )
        job_id = res.json()['job_id']
        for k in range(30):
            res = requests.get(
                f'{self.url}/anchored_top_k?job_id={job_id}', 
                headers=headers,
            )
            res = res.json()
            if res['status'] == 'success':
                return res['result']
            elif res['status'] == 'error':
                raise ValueError(res['message'])
            sleep(3)
        raise ValueError('Timeout')
    
    @classmethod
    def get_new(cls, url = 'https://lucario.deepdocs.net', name: str = 'New Knowledge Base'):
        LUCARIO_MASTER_KEY = os.environ.get('LUCARIO_MASTER_KEY')
        if not LUCARIO_MASTER_KEY:
            raise ValueError("LUCARIO_MASTER_KEY environment variable is not set.")
        headers = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
        }

        response = requests.post(
            f'{url}/projects/create/{quote(name)}/{quote(LUCARIO_MASTER_KEY)}',
            headers=headers,
        )
        result = response.json()
        return cls(url = url, project_id = result['key']['value'])
    
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