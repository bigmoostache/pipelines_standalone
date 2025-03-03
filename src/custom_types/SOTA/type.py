from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Dict, Optional, Tuple, Union, Literal, ClassVar
from datetime import datetime
import json
from custom_types.LUCARIO.type import LUCARIO, Document, FileTypes, ForceChunk
from time import time
from uuid import uuid4
import requests
import re

from bs4 import BeautifulSoup

def extract_references(html):
    soup = BeautifulSoup(html, 'html.parser')
    references = soup.find_all('reference')
    results = []
    for ref in references:
        # Get the 'informationid' attribute; returns None if not found.
        informationid = ref.get('informationid')
        # Get the 'position' attribute; if not present, default to None.
        position = ref.get('position', None)
        
        results.append({
            'informationid': int(informationid),
            'position': position
        })
    return results

class VersionedText(BaseModel):
    versions      : Dict[int, str] = Field(..., description = "version_id -> text value until next version. Key = None if modified but not stored in last version not saved yet")
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

class Congiguration(BaseModel):
    textColor : str
    boldColor : str
    titleColor : str
    font : str
    language : str    

class Sections(BaseModel):
    enumeration : str
    sections    : List[Tuple[bool, int]] = Field(..., description = "Tuple[Section Name, Whether to show this section name, information_id]")
    class_name : ClassVar[str] = 'Sections'
    
class Referencement(BaseModel):
    information_id : int              = Field(..., description = "information_id")
    detail         : str              = Field(..., description = "Very short detail about where exactly in the information to look (eg: the page number, t)")
    analysis       : str              = Field(..., description = "Analysis of the reference w.r.t. this information.")
    pertinence     : float
    
def __str__(self):
    return f"Sections: {self.sections}"   
class VersionedInformation(BaseModel):
    
    class PlaceHolder(BaseModel):
        class_name : ClassVar[str] = 'PlaceHolder'
        def __str__(self):
            return "PlaceHolder, empty for now"
        
    class External(BaseModel):
        external_db : str                 = Field(..., description = "Database, provider, api, whatever. Must match an implemented algorithm.")
        external_id : Union[str, float]           = Field(..., description = "External identifier. May be anything. Unlike the Sections model, conceptually, the information here is not just the id, it is also the information behind the underlying entity.")
        class_name : ClassVar[str] = 'External'
        
        def __str__(self):
            return f"External: {self.external_db} - {self.external_id}"

    versions: Dict[int, Union[PlaceHolder, Sections, External, str]] = Field(..., description="Content of the versioned information. The key is the version id.")
    
    referencements : Dict[int, Referencement]     = Field(..., description = "local_referencement_id -> Referencement")
    referencement_versions : Dict[int, List[int]] = Field(..., description = "version_id -> List[local_annotation_id]")

    title    : VersionedText
    abstract : VersionedText
    reference_as : VersionedText = Field(..., description = "If you reference this section, this reference_as string will appear")
    
    annotations : Dict[int, VersionedText]    = Field(..., description = "local_annotation_id -> Annotation")
    active_annotations : Dict[int, List[int]] = Field(..., description = "version_id -> List[local_annotation_id]")
    ai_pipelines_to_run : List[str]           = Field(..., description = "List of AI pipelines to run on this information")
    
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
    
    def exists_in_stack(self : 'VersionedInformation', versions_list : List[int]) -> bool:
        last = SOTA.get_last(self.versions, versions_list, return_id = True)
        return last is not None
    
    @staticmethod
    def get_class_name(
        x : Union[PlaceHolder, Sections, External, str]
        ) -> Literal['PlaceHolder', 'Sections', 'Image', 'Table', 'External', 'str', 'Paragraphs']:
        if isinstance(x, str):
            return 'str'
        return x.class_name
        
class SOTA(BaseModel):
    title              : VersionedText      = Field(..., description = "Document title")
    drop_url           : str
    file_id            : str
    pipeline_id        : Union[int, None]   = Field(None, description = "The pipeline id that is currently running on the document. None if no pipeline is running.")
    
    versions           : Dict[int, Version] = Field(..., description = "version_id -> Version")
    current_version_id : int                = Field(..., description = "version_id of the currently featured version.")
    
    authors            : Dict[int, Author]  = Field(..., description = "author_id -> Author")
    active_authors     : Dict[int, List[int]] = Field(..., description = "version_id -> List[author_id]")

    information        : Dict[int, VersionedInformation] = Field(..., description = "information_id -> VersionedInformation")
    mother_id          : int                  = Field(..., description = "Master information for the rendering")
    bibliography       : Dict[int, List[int]] = Field(..., description = "version_id -> List[information_id]")
    
    configuration : Congiguration = Field(..., description = "Document configuration")
    
    translations : ClassVar[Dict[str, Dict[str, str]]] = {
        'title': {'fr': 'Titre', 'en': 'Title'},
        'comment': {'fr': 'Commentaire', 'en': 'Comment'},
        'start': {'en': 'START OF FOCUS', 'fr': 'DEBUT DU FOCUS'},
        'end': {'en': 'END OF FOCUS', 'fr': 'FIN DU FOCUS'},
        'expectations': {'en': 'Expectations in substance and form', 'fr': 'Attentes en fond et en forme'},
    }
    
    def t(self, key : str, translations: dict = None) -> str:
        translations = translations if translations else self.translations
        lang = self.configuration.language
        if lang == 'us':
            lang = 'en'
        return translations[key].get(lang, translations[key]['en'])
    
    def get_leaf_children(self : 'SOTA', information_id : int, version_list : List[int]) -> List[int]:
        last = self.get_last(self.information[information_id].versions, version_list)
        if VersionedInformation.get_class_name(last) == 'Sections':
            return [_ for _ignore, __ in last.sections for _ in self.get_leaf_children(__, version_list)]
        elif VersionedInformation.get_class_name(last) == 'PlaceHolder':
            return []
        return [information_id]
    
    @classmethod
    def get_empty(cls) -> 'SOTA':
        return cls(
            title = VersionedText(versions = {1: "New Document"}),
            drop_url = "https://lucario.croquo.com/files",
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
    
    def build_text(
        self : 'SOTA', 
        version : int = None, 
        information_id : int = None, 
        focused_information_id : int = None,
        depth : int = 0) -> str:
        # 1. Get the latest version of the information
        version, information_id = -1 if version is None else version, self.mother_id if information_id is None else information_id
        versions_list = self.versions_list(version)
        info = self.information[information_id]
        # 2. Get the latest version of the title and abstract
        get_last = lambda x : SOTA.get_last(x, versions_list)
        latest_content, title, abstract = get_last(info.versions), get_last(info.title.versions), get_last(info.abstract.versions)
        # 3. Get the latest version of the content
        if info.get_class_name(latest_content) == 'str':
            content = latest_content
        elif info.get_class_name(latest_content) == 'PlaceHolder':
            content = ''
        elif info.get_class_name(latest_content) == 'Sections':
            content = '\n\n'.join([self.build_text(version, subsection_id, focused_information_id = focused_information_id, depth = depth + 1) for _, subsection_id in latest_content.sections])
        # 4. Get the latest version of the annotations
        if focused_information_id == information_id:
            annotations = get_last(info.active_annotations) or []
            annotations = [get_last(info.annotations[_].versions) for _ in annotations]
            annotations = '\n'.join([f'<!--\n{self.t("comment")} n°{i+1} - {annotation}\n-->' for i, annotation in enumerate(annotations)]) + '\n'
        else:
            annotations = ''
        # 5. Build the text
        start = f'<!-- >>>>>>>>>>>>>>>> {self.t("start")} -->\n' if focused_information_id == information_id else ''
        end = f'<!-- <<<<<<<<<<<<<<<< {self.t("end")} -->\n' if focused_information_id == information_id else ''
        abstract = f'<!--\n{self.t("expectations")} - {abstract}\n-->\n' if abstract else ''
        title = f'<h{depth+1}>{title}</h{depth+1}>\n' if title else ''
        text = f'{start}{title}{abstract}{content}{annotations}{end}'
        # 6. Return the text with the correct prefix to indicate the focus
        prefix1 = '>>>' if focused_information_id == information_id else ''
        prefix2 = '\t' if depth > 0 else ''
        prefix = prefix1 + prefix2
        return (prefix.join([''] + text.splitlines(True))).replace('\t>>>', '>>>\t') 

    def build_references(
        self : 'SOTA', 
        information_id: int,
        allow_external: bool = True,
        force_keep_documents: bool = True,
        force_keep_chunks: bool = True
        ) -> List[dict]:
        # Retrieve the relevant information and initialize Lucario for API interactions.
        info = self.information[information_id]
        version_list = self.versions_list(-1)
        leaf_nodes = self.get_leaf_children(information_id, version_list)
        
        referenced_documents: Dict[int, List[int]] = {} # information_id -> information_id
        referenced_chunks: Dict[int, List[Tuple[int, int]]] = {} # information_id -> (information_id, file_id in lucario for chunk)
        text_chunks: Dict[int, List[str]] = {} # information_id -> List[str]
        
        for information_id in leaf_nodes:
            info = self.information[information_id]
            # Extract in-text references from the built text.
            intext_references = extract_references(self.build_text(information_id=information_id))
            versions_list = self.versions_list(-1)
            structure_references = SOTA.get_last(info.referencement_versions, versions_list) or []
            structure_references = [info.referencements[_] for _ in structure_references]
            structure_references = [{'informationid': ref.information_id, 'position': _.strip()} for ref in structure_references for _ in (ref.detail + ',').split(',')]
            
            # Combine both extracted and structured references, filtering out duplicates and empty positions.
            all_references = intext_references + structure_references
            all_information_ids = list(set([_['informationid'] for _ in all_references]))
            references = []
            found_pairs = set()
            for ref in structure_references:
                if (ref['informationid'], information_id) in found_pairs:
                    continue
                found_pairs.add((ref['informationid'], ref['position']))
                if ref['position'] not in {None, ''}:
                    references.append(ref)
                    
            # Save those
            referenced_documents[information_id] = all_information_ids
            referenced_chunks[information_id] = references
            text_chunks[information_id] = [
                self.build_text(information_id=information_id),
                self.get_last(info.title.versions, version_list) + self.get_last(info.abstract.versions, version_list),
                self.get_last(info.versions, version_list)
            ]
        # Build Lucario out of that
        lucario = LUCARIO(url=self.drop_url, project_id=self.file_id, elements={}, uuid_2_position={})
        lucario.update()
        lucario_file_id_to_information_id = {v.file_id: k for k,v in lucario.elements.items()}
        # Now, the important part: the logic of how to build the similarity requests
        if allow_external:
            # in that case, all documents may be used
            file_uuids = [document.file_uuid for document in lucario.elements.values()]
        else:
            # otherwise, only the documents already used may be used
            all_referenced_documents = list(set([_ for i, chunks in referenced_documents.items() for _ in chunks]))
            file_uuids = [lucario.elements[_].file_uuid for _ in all_referenced_documents]
        files_forces = []
        if force_keep_documents:
            # this will force chunks from referenced documents to be used
            files_forces += [ForceChunk(file_uuid = lucario.elements[ref_id].file_uuid, group_id = str(i))
                             for i,_ in referenced_documents.items()
                             for ref_id in _ 
                             if ref_id in lucario.elements
                             ]
        if force_keep_chunks:
            # this will force specific chunks to be used
            files_forces += [ForceChunk(file_uuid = lucario.elements[ref_id].file_uuid, group_id = str(i), chunk_id = chunk_id)
                             for i,_ in referenced_chunks.items()
                             for ref_id,chunk_id in _
                             if ref_id in lucario.elements
                             ]
        res = lucario.anchored_top_k(
            queries = [_ for i, chunks in text_chunks.items() for _ in chunks],
            group_ids = [i for i, chunks in text_chunks.items() for _ in chunks],
            max_groups_per_element=2,
            elements_per_group=50,
            min_elements_per_list=3,
            file_uuids=file_uuids,
            files_forced=files_forces
        )
        for _ in res:
            _['referenced_information'] = lucario_file_id_to_information_id[_['parent_file_id']]
            _['reference'] = lucario.elements[_['referenced_information']].description
            _['chunk_id'] = _['file_id']
        return res


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
        # That price is in rockets 🚀, which is an abstraction
        pipeline_prices = {
            'rewrite': 7,
            'brush': 1,
            'translate': 1,
            'make_longer': 1,
            'make_shorter': 1,
            'rewrite_expectations': 2,
            'provide_feedback': 2,
            'sections_rewrite_expectations': 2,
            'rebuild_sections': 2,
            'sections_feedback': 2,
            'sections_references': 1,
            'write_bibliography': 2
        }
        return sum([pipeline_prices.get(json.loads(pipeline).get('name', ''), 1) for _ in doc.information.values() for pipeline in _.ai_pipelines_to_run])
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='sota',
    _class = SOTA,
    converter = Converter,
    visualiser = "https://sota2.deepdocs.net",
    icon='/icons/ai.svg'
)