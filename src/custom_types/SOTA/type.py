from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Dict, Optional, Tuple, Union, Literal, ClassVar
from datetime import datetime
import json
from time import time
from uuid import uuid4
import requests
import re

class VersionedText(BaseModel):
    versions      : Dict[int, str] = Field(..., description = "version_id -> text value until next version. Key = None if modified but not stored in last version not saved yet")
class VersionedFloat(BaseModel):
    versions      : Dict[int, float] = Field(..., description = "version_id -> float value")
class VersionedListVersionedText(BaseModel):
    entries       : Dict[int, VersionedText]
    versions      : Dict[int, List[int]]

class Version(BaseModel):
    date                : str        = Field(..., description="Version save date - ISO 8601")
    description         : str        = Field(..., description="Update description")
    digest              : str        = Field(..., description="Document digest")
    blame_author_id     : int        = Field(..., description="Author to blame")
    previous_version_id : Optional[int] = Field(..., description="ID of parent version. If None, then initializes a tree.")

class Author(BaseModel):
    name                : VersionedText = Field(..., description = "Author name")
    role                : VersionedText = Field(..., description = "Author role for the document and in general")
    current_affiliations: VersionedListVersionedText = Field(..., description = "Author affiliated institutions and organizations")
    contact_information : VersionedText = Field(..., description = "Useful information to contact the author")

class SignHere(BaseModel):
    class Signature(BaseModel):
        author_id      : int      = Field(..., description="Signatory author_id")
        version_signed : int      = Field(..., description="The version at which the signature was made")
        public_key     : str      = Field(..., description="Signatory public key")
        signature      : str      = Field(..., description="Signature")
    role        : VersionedText   = Field(..., description="The role associated with the signature")
    description : VersionedText   = Field(..., description="A brief description of the role or context of the signature")
    signatures  : List[Signature] = Field(..., description="Signatures. Old ones are kept")

class Keyword(BaseModel):
    abbreviation : VersionedText = Field(..., description="The abbreviated form of the keyword")
    definition   : VersionedText = Field(..., description="The full definition of the keyword")

class FormatedText(BaseModel):
    text : str
    format : Literal["text", "markdown", "json", "latex", "code"]
    class_name : ClassVar[str] = 'FormatedText'
    
    def __str__(self):
        return f"```{self.format}\n{self.text}\n```"
    
class Embedder(BaseModel):
    # pikabu will embed this content in the document
    information_id : int
    section_id : str
    content : str
    context : str
      
class Congiguration(BaseModel):
    textColor : str
    boldColor : str
    titleColor : str
    font : str
    language : str    
      
class VersionedInformation(BaseModel):
    class Paragraphs(BaseModel):
        paragraphs : List[FormatedText]
        class_name : ClassVar[str] = 'Paragraphs'
        
        def __str__(self):
            return '\n\n'.join(str(_) for _ in self.paragraphs)
        
    class PlaceHolder(BaseModel):
        class_name : ClassVar[str] = 'PlaceHolder'
        
        def __str__(self):
            return "PlaceHolder, empty for now"
        
    class Sections(BaseModel):
        enumeration : Literal["Numbers enumeration", "Latin enumeration", "Lowercase letters enumeration", "Capital letters enumeration", "Concatenation"] = Field(..., description = "Wheter to enumerate or itemize")
        sections    : List[Tuple[bool, int]] = Field(..., description = "Tuple[Section Name, Whether to show this section name, information_id]")
        class_name : ClassVar[str] = 'Sections'
        
        def __str__(self):
            return f"Sections: {self.sections}"
        
    class Image(BaseModel):
        url         : str                 = Field(..., description = "Image public url")
        label       : str                 = Field(..., description = "Image label")
        class_name : ClassVar[str] = 'Image'
        
        def __str__(self):
            return f"Image: {self.label}"
        
    class Table(BaseModel):
        csv             : str             = Field(..., description = "utf-8 encoded csv, with columns.")
        column_groups   : List[str]       = Field(..., description = "List of column names to aggregated rows by, in the right order. Can be empty.")
        column_hierarcy : dict            = Field(..., description = "Tree. Each node is a string. Leafs are column names. Will aggregate columns according to that tree. Non found columns will be isolated.")
        class_name : ClassVar[str] = 'Table'
        
        def __str__(self):
            return f"```csv\n{self.csv}\n```"
        
    class External(BaseModel):
        external_db : str                 = Field(..., description = "Database, provider, api, whatever. Must match an implemented algorithm.")
        external_id : Union[str, float]           = Field(..., description = "External identifier. May be anything. Unlike the Sections model, conceptually, the information here is not just the id, it is also the information behind the underlying entity.")
        class_name : ClassVar[str] = 'External'
        
        def __str__(self):
            return f"External: {self.external_db} - {self.external_id}"

    versions: Dict[int, Union[PlaceHolder, Sections, Image, Table, External, str, Paragraphs, FormatedText]] = Field(..., description="Content of the versioned information. The key is the version id.")

    class Referencement(BaseModel):
        information_id : int              = Field(..., description = "information_id")
        detail         : str              = Field(..., description = "Very short detail about where exactly in the information to look (eg: the page number, t)")
        analysis       : str              = Field(..., description = "Analysis of the reference w.r.t. this information.")
        pertinence     : float
        
    referencements : Dict[int, Referencement]     = Field(..., description = "local_referencement_id -> Referencement")
    referencement_versions : Dict[int, List[int]] = Field(..., description = "version_id -> List[local_annotation_id]")

    title    : VersionedText
    abstract : VersionedText
    reference_as : VersionedText = Field(..., description = "If you reference this section, this reference_as string will appear")
    
    annotations : Dict[int, VersionedText]    = Field(..., description = "local_annotation_id -> Annotation")
    active_annotations : Dict[int, List[int]] = Field(..., description = "version_id -> List[local_annotation_id]")
    ai_pipelines_to_run : List[str]           = Field(..., description = "List of AI pipelines to run on this information")
    
    # this below is a bit special.
    embeddings : Dict[int, List[str]] = Field(..., description = "version_id -> List[section_id]")

    def retrieve_reference_id(self, referenced_information_id):
        for ref_id, ref in self.referencements.items():
            if ref.information_id == referenced_information_id:
                return ref_id
        return None

    def update_embeddings(self, versions_list : List[int], embedders : List[Embedder]):
        last_id = SOTA.get_last(self.versions, versions_list, return_id = True)
        if last_id is None: return
        self.embeddings = {
            last_id : [embedder.section_id for embedder in embedders]
        }
    def embeddings_are_up_to_date(self, versions_list : List[int]):
        assert len(versions_list) > 0
        last_version_id = SOTA.get_last(self.versions, versions_list, return_id = True)
        if (last_version_id is None) or (last_version_id == -1) or (last_version_id != versions_list[0]): return False
        return True
    
    @classmethod
    def create_text(cls, title : str = '', contents : str = '', abstract : str = '', reference_as : str = None):
        return cls(
            versions = {-1 : contents},
            referencements = {},
            referencement_versions = {-1:[]},
            title = VersionedText(versions={-1:title}),
            abstract = VersionedText(versions={-1:abstract}),
            reference_as = VersionedText(versions={-1:reference_as if reference_as else title}),
            annotations = {},
            active_annotations = {-1:[]},
            ai_pipelines_to_run = [],
            embeddings = {}
        )
        
    def get_last_version(
        self : 'VersionedInformation', 
        versions_list : List[int]
        ):
        return SOTA.get_last(self.versions, versions_list)
    def get_all_children_ids(
        self : 'VersionedInformation', 
        sota : 'SOTA', 
        my_id : int,
        versions_list : List[int]) -> Dict[int, Union[None, int]]:
        last = self.get_last_version(versions_list)
        if isinstance(last, self.Sections):
            section_ids = [__ for _, __ in last.sections]
            res = {_ : my_id for _ in section_ids}
            for section_id in section_ids:
                section = sota.information[section_id]
                res.update(section.get_all_children_ids(sota, section_id, versions_list))
            return res
        return {}
    def exists_in_stack(self : 'VersionedInformation', versions_list : List[int]) -> bool:
        last = SOTA.get_last(self.versions, versions_list, return_id = True)
        return last is not None
    
    @staticmethod
    def get_class_name(
        x : Union[PlaceHolder, Sections, Image, Table, External, str, Paragraphs, FormatedText]
        ) -> Literal['PlaceHolder', 'Sections', 'Image', 'Table', 'External', 'str', 'Paragraphs']:
        if isinstance(x, str):
            return 'str'
        return x.class_name
    
    def print_reference(
        self: 'VersionedInformation',
        referencement_id : int,
        sota : 'SOTA',
        versions_list : List[int]
    ) -> str:
        reference = self.referencements[referencement_id]
        _information = sota.information[reference.information_id]
        information = sota.get_last(_information.versions, versions_list)
        if information.get_class_name(_information) == 'External':
            raise "External references are not supported"
        else:
            return information.text_representation(
                reference.information_id, 
                sota, 
                versions_list, 
                detail = reference.detail, 
                include_title = True, 
                include_abstract = False, 
                include_content = True, 
                include_annotations = False, 
                include_referencements = 0)
        
    def lucario_get_chunk(
        self : 'VersionedInformation',
        sota : 'SOTA',
        versions_list : List[int],
        detail : str
    ) -> str:
        # In this case, detail is the file_id in the lucario 🦊 database
        headers = {'accept': 'application/json' }
        params = {'file_id': str(detail)}
        if not str(detail):
            last = self.get_last_version(versions_list)
            params['file_uuid'] = last.external_id
        url = re.sub(r'/files', '/chunk', sota.drop_url)
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return []
        documents : List[Document] = [Document.model_validate(_) for _ in response.json()]
        res = ''
        for document in documents:
            if document.file_ext == 'image_desc':
                res += f'Image: {document.description}\n'
            else:
                if document.context:
                    res += 'Context: ' + document.context + '\n'
                if document.description:
                    res += 'Description: ' + document.description + '\n'
                if document.text:
                    res += 'Text: ' + document.text + '\n'
            res += '---\n'
        return res
    
    def access_external(
        self : 'VersionedInformation',
        my_id : int,
        sota : 'SOTA',
        versions_list : List[int],
        detail : str
    ) -> str:
        last = self.get_last_version(versions_list)
        assert self.get_class_name(last) == 'External'
        if last.external_db == 'file':
            return self.lucario_get_chunk(sota, versions_list, detail)
        raise "External references are not supported"
        
    def text_representation(
        self : 'VersionedInformation',
        my_id : int,
        sota : 'SOTA',
        versions_list : List[int],
        detail : str = '',
        include_title : bool = True,
        include_abstract : bool = False,
        include_content : bool = False,
        include_annotations : bool = False,
        include_referencements : int = 0,
        include_parent_context : bool = False,
        mode : Literal['reference', 'context', 'normal'] = 'normal'
    ) -> str:
        gl = lambda x : sota.get_last(x, versions_list)
        if mode == 'reference':
            bs = lambda contents, emoji, title : f'{title}: {contents}\n'
        else:
            bs = lambda contents, emoji, title : f'\n//\n// {emoji}{emoji}{emoji} {title}\n//:\n{contents}\n' 
        ############################################################
        ############################################################
        if mode == 'context':
            # return the title plus the abstract. if no abstract, replace with contents
            r = '' + gl(self.title.versions) + '\n'
            abstract = gl(self.abstract.versions)
            if abstract:
                r += abstract
            else:
                last = self.get_last_version(versions_list)
                contents = str(last).replace('\n\n', '\n').replace('\n\n', '\n')
                r += contents
            return r
        ############################################################
        r = ''
        if include_parent_context:
            mother = sota.information[sota.mother_id]
            active_ids = mother.get_all_children_ids(sota, sota.mother_id, versions_list)
            active_ids[sota.mother_id] = None
            parent_id = active_ids[my_id]
            if parent_id:
                parent = sota.information[parent_id]
                parent_version = gl(parent.versions).sections
                cousin_ids = [__ for _, __ in parent_version]
                if len(cousin_ids) > 1:
                    contents = ''
                    for cousin_id in cousin_ids:  
                        prexix = '[ ==> 🔎 CURRENT SECTION 🔎 <== ] ' if cousin_id == my_id else '[COUSIN SECTION] ' 
                        contents += prexix + sota.information[cousin_id].text_representation(my_id, sota, versions_list, mode = 'context') + '\n\n'
                    r += bs(contents, '🚧', 'Structure of parent section. Use it to favor contistency, continuity, coherence, and avoid redundancy')
        if include_title:
            r += bs(gl(self.title.versions), '📚', 'Title')
        if include_abstract:
            abstract = sota.get_last(self.abstract.versions, versions_list)
            if abstract:
                r += bs(abstract, '🧑‍🍳', 'Attendus, expectations')
        if include_referencements:
            last = gl(self.referencement_versions)
            last = last if last else []
            last = [(_, self.referencements[_]) for _ in last]
            last.sort(key = lambda x: x[1].pertinence, reverse = True)
            last = last[:include_referencements]
            if last:
                contents = ''
                for ref_local_id, referencement in last:
                    reference_information = sota.information[referencement.information_id]
                    reference_text = reference_information.text_representation(
                        referencement.information_id, 
                        sota, 
                        versions_list, 
                        detail = referencement.detail, 
                        include_title = True, 
                        include_abstract = False, 
                        include_content = True, 
                        include_annotations = False, 
                        include_referencements = 0,
                        mode='reference'
                        )
                    if referencement.analysis:
                        reference_text += '\n' + referencement.analysis
                    reference_text = '\t' + reference_text.replace('\n', '\n\t')
                    contents += f'  - [[{ref_local_id}]] (Cite this by writing [[{ref_local_id}]]) \n{reference_text}\n'
                r += bs(contents, '📄', 'Sources and references')
        if include_content:
            last = self.get_last_version(versions_list)
            if self.get_class_name(last) != 'External':
                contents = str(last)
                if contents:
                    r += bs(contents, '🖊️', 'Contents')
            else:
                contents = self.access_external(my_id, sota, versions_list, detail)
                r += bs(contents, '🔗', 'Contents')
        if include_annotations:
            actives = gl(self.active_annotations)
            actives = actives if actives else []
            annotations = [gl(self.annotations[_].versions) for _ in actives]
            if annotations:
                r += bs('\n'.join(annotations), '💬', 'Comments and feedbacks; take them into account. Directives situated here prevail on ANYTHING ELSE. Here are the actual requests of the user, so FOCUS ON THEM!')
        return r
    
pipelines = {
    'dummy': ['FormattedText', 'Sections', 'Image', 'Table', 'External', 'Paragraphs', 'PlaceHolder', 'str'],
    'Attendu': ['FormattedText', 'Sections', 'Image', 'Table', 'External', 'Paragraphs', 'PlaceHolder', 'str'],
    'Find references': ['FormattedText', 'Sections', 'Image', 'Table', 'External', 'Paragraphs', 'PlaceHolder', 'str'],
    'Analyse References': ['FormattedText', 'Sections', 'Image', 'Table', 'External', 'Paragraphs', 'PlaceHolder', 'str'],
    'Write': ['Paragraphs', 'FormattedText', 'str'],
    'Suggest AI pipelines': ['FormattedText', 'Sections', 'Image', 'Table', 'External', 'Paragraphs', 'PlaceHolder', 'str'],
    'Rewrite subsections': ['PlaceHolder', 'Sections', 'str'],
    'Extract data': ['Table'],
    'Create subsections': ['PlaceHolder', 'Sections', 'str']
}
    
class SOTA(BaseModel):
    title              : VersionedText      = Field(..., description = "Document title")
    drop_url           : str
    pikabu_url         : str
    file_id            : str
    pipeline_id        : Union[int, None]   = Field(None, description = "The pipeline id that is currently running on the document. None if no pipeline is running.")
    
    versions           : Dict[int, Version] = Field(..., description = "version_id -> Version")
    current_version_id : int                = Field(..., description = "version_id of the currently featured version.")
    
    authors            : Dict[int, Author]  = Field(..., description = "author_id -> Author")
    active_authors     : Dict[int, List[int]] = Field(..., description = "version_id -> List[author_id]")
    signatures         : List[SignHere]     = Field(..., description = "A list of signatures related to the Document.")
    keywords           : Dict[int, Keyword] = Field(..., description = "A list of keywords used globally in the Document.")

    information        : Dict[int, VersionedInformation] = Field(..., description = "information_id -> VersionedInformation")
    mother_id          : int                  = Field(..., description = "Master information for the rendering")
    bibliography       : Dict[int, List[int]] = Field(..., description = "version_id -> List[information_id]")
    
    configuration : Congiguration = Field(..., description = "Document configuration")
    
    @classmethod
    def get_empty(cls) -> 'SOTA':
        return cls(
            title = VersionedText(versions = {1: "New Document"}),
            drop_url = "https://lucario.croquo.com/files",
            pikabu_url = "https://pikabu.croquo.com",
            file_id = str(time())+'.'+str(uuid4()),
            pipeline_id = None,
            versions = {
                1:
                    Version(
                        date = datetime.now().isoformat(),
                        description = "Initial version",
                        digest = "Initial version",
                        blame_author_id = 1,
                        previous_version_id = None
                    )
            },
            current_version_id = 1,
            authors = {1:Author(
                name = VersionedText(versions={1:"Author"}),
                role = VersionedText(versions={1:"Writer"}),
                current_affiliations = VersionedListVersionedText(entries = {}, versions = {1 : []}),
                contact_information = VersionedText(versions={1:""})
            )},
            active_authors = {1:[1]},
            signatures = [],
            keywords = {},
            information = {
                1 : VersionedInformation.create_text(contents = {}, title = 'Body', reference_as = 'Body')
            },
            mother_id = 1,
            bibliography = {1:[]},
            configuration = Congiguration(
                textColor = '#1e1b4b',
                titleColor = '#4f46e5',
                boldColor = '#a16207',
                font = 'Calibri',
                language = 'us'
            )
        )
    
    def versions_list(self : 'SOTA', version : int):
        if version == -1:
            version = self.current_version_id
            versions = [-1, version]
        else:
            versions = [version]
        if version not in self.versions:
            raise "Version does not exist"
        while True:
            v = self.versions[version]
            if v.previous_version_id is None:
                return versions
            versions.append(v.previous_version_id)
            version = v.previous_version_id
    @staticmethod
    def get_new_id(something):
        i = max(len(something), 1)
        while i in something:
            i += 1
        return i
    
    @staticmethod
    def get_last(something, versions_list, return_id = False):
        for version in versions_list:
            if version in something:
                if return_id:
                    return version
                return something[version]
        return None

    def top_k(self, query : str, k : int = 10, information_ids : List[int] = [], max_per_information : int = 0):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        json_data = {
            'file_id': self.file_id,
            'query_text': query,
            'k': k,
            'information_ids': information_ids,
            'max_per_information': max_per_information,
        }
        response = requests.post(f'{self.pikabu_url}/top_k', headers=headers, json=json_data)
        r = response.json()
        return r
    
    def embed(self, embedders : List[Embedder]):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        params = {
            'file_id': self.file_id,
        }
        json_data = [
            {
                'information_id': embedder.information_id,
                'section_id': embedder.section_id,
                'content': embedder.content,
                'context': embedder.context,
            }
            for embedder in embedders
        ]
        response = requests.post(f'{self.pikabu_url}/embed', params=params, headers=headers, json=json_data)
        
        response.raise_for_status()

class Converter:
    @staticmethod
    def to_bytes(doc : SOTA) -> bytes:
        return doc.model_dump_json(indent=2).encode('utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> SOTA:
        return SOTA.parse_obj(json.loads(b.decode('utf-8')))
    @staticmethod
    def str_preview(doc: SOTA) -> str:
        return doc.model_dump_json(indent=2)[:10000]
    @staticmethod
    def len(doc: SOTA) -> int:
        # number of pipelines to run
        return sum([len(doc.information[_].ai_pipelines_to_run) for _ in doc.information])
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='sota',
    _class = SOTA,
    converter = Converter,
    visualiser = "https://sota2.deepdocs.net",
    icon='/icons/ai.svg'
)



################## Lucario 🦊 ##################

from pydantic import BaseModel
from datetime import datetime 
from typing import Literal, Union, Optional, List
from enum import Enum

class FileTypes(str, Enum):
    txt = 'txt'
    pdf = 'pdf'
    png = 'png'
    jpg = 'jpg'
    jpeg = 'jpeg'
    word = 'docx'
    msword = 'doc'
    ppt = 'ppt'
    pptx = 'pptx'
    csv = 'csv'
    
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
    file_id: int
    parent_file_id : Optional[int]
    direct_parent_file_id : Optional[int]
    file_uuid : str
    file_name : str
    file_hash : str
    file_ext : FileTypes
    upload_date : datetime
    pipeline_status : PipelineStatus
    ext_project_id : str
    
    context : Optional[str] # To situate within the parent document, e.g. a paragraph number
    position : Optional[int] # To order within the parent document
    description : Optional[str] # For root documents: a description of the document
    
    # The two below are not expected to be files in the database.
    text : Optional[str] # For textualizable documents: the text content
    score : Optional[float] # For documents with scores, e.g. relevance
    raw_url : Optional[str] # Provided to the user for download
    
class TopkDocument(BaseModel):
    main_document : Document
    n_chunks : int
    chunks : List[Document]
    
class TopkResult(BaseModel):
    embedding_time : float
    search_time : float
    retrieval_time : float
    top_k_documents : List[TopkDocument]

def get_topk(
    project_id : str,
    query_text: str,
    k : int,
    drop_url : str,
    file_uuids : List[str] = [],
    max_per_information : int = 0,
    ) -> TopkResult:
    url = re.sub(r'/files', '/top_k', drop_url)
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    
    json_data = {
        'project_id': project_id,
        'query_text': query_text,
        'k': k,
        'file_uuids': file_uuids,
        'max_per_information': max_per_information,
    }
    
    response = requests.post(url, headers=headers, json=json_data)
    
    return TopkResult.model_validate(response.json())

def get_chunks(
    file_ids : str, # comma separated
    drop_url : str
    ) -> List[Document]:
    headers = {
        'accept': 'application/json',
    }

    params = {
        'file_id': file_ids,
    }
    url = re.sub(r'/files', '/chunk', drop_url)
    response = requests.get(url, params=params, headers=headers)
    return [Document.model_validate(_) for _ in response.json()]