from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Dict, Optional, Tuple, Union, Literal, ClassVar
from datetime import datetime
import json
from custom_types.LUCARIO.type import LUCARIO, Document, FileTypes, ForceChunk
from time import time
from uuid import uuid4
from enum import Enum
from pipelines.CONVERSIONS.DICT.to_html import Pipeline as DictToHtmlPipeline
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

class Sections(BaseModel):
    sections    : List[int] = Field(..., description = "Information ids")
    class_name : ClassVar[str] = 'Sections'
    
class Referencement(BaseModel):
    information_id : int              = Field(..., description = "information_id")
    detail         : str              = Field(..., description = "Very short detail about where exactly in the information to look (eg: the page number, t)")
    analysis       : str              = Field(..., description = "Analysis of the reference w.r.t. this information.")
    
def __str__(self):
    return f"Sections: {self.sections}"   

class LucarioElement(BaseModel):
    lucario_id : int = Field(..., description = "Identifier of the Lucario Information inside the SOTA document")
    local_document_identifier : int = Field(..., description = "Identifier of the document in the Lucario database")

class VersionedInformation(BaseModel):
    class PlaceHolder(BaseModel):
        class_name : ClassVar[str] = 'PlaceHolder'
        def __str__(self):
            return "PlaceHolder, empty for now"
        
    versions: Dict[int, Union[PlaceHolder, Sections, str, LUCARIO, LucarioElement]] = Field(..., description="Content of the versioned information. The key is the version id.")
    
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
        x : Union[PlaceHolder, Sections, LUCARIO, LucarioElement, str]
        ) -> Literal['PlaceHolder', 'Sections', 'LUCARIO', 'LucarioElement', 'str']:
        if isinstance(x, str):
            return 'str'
        return x.__class__.__name__
    
class Language(Enum):
    fr = 'fr'
    en = 'en'
    us = 'us'
    gb = 'gb'
        
class SOTA(BaseModel):
    title              : VersionedText      = Field(..., description = "Document title")
    pipeline_id        : Union[int, None]   = Field(None, description = "The pipeline id that is currently running on the document. None if no pipeline is running.")
    
    versions           : Dict[int, Version] = Field(..., description = "version_id -> Version")
    current_version_id : int                = Field(..., description = "version_id of the currently featured version.")
    
    authors            : Dict[int, Author]  = Field(..., description = "author_id -> Author")
    active_authors     : Dict[int, List[int]] = Field(..., description = "version_id -> List[author_id]")

    information        : Dict[int, VersionedInformation] = Field(..., description = "information_id -> VersionedInformation")
    main_lucario_id    : int                  = Field(..., description = "Information id of the LUCARIO element to use as the main knowledge base")
    mother_id          : int                  = Field(..., description = "Master information for the rendering")
    
    styles_sheet       : VersionedText        = Field(..., description = "CSS sheet for the document")
    language           : Language             = Field(..., description = "Language of the document")
    
    translations : ClassVar[Dict[str, Dict[str, str]]] = {
        'title': {'fr': 'Titre', 'en': 'Title'},
        'comment': {'fr': 'Commentaire', 'en': 'Comment'},
        'start': {'en': 'START OF FOCUS', 'fr': 'DEBUT DU FOCUS'},
        'end': {'en': 'END OF FOCUS', 'fr': 'FIN DU FOCUS'},
        'expectations': {'en': 'Attendus', 'fr': 'Expectations'},
    }
    
    def t(self, key : str, translations: dict = None) -> str:
        translations = translations if translations else self.translations
        lang = self.language
        if lang == 'us':
            lang = 'en'
        return translations[key].get(lang, translations[key]['en'])
    
    def update_lucario(self : 'SOTA', lucario_information_id: int = None):
        if lucario_information_id is None:
            lucario_information_id = self.main_lucario_id
        lucario = self.information[lucario_information_id].get_last_version(self.versions_list(-1))
        assert isinstance(lucario, LUCARIO), "The information is not a LUCARIO element"
        lucario.update()
        mapping = {}
        for local_id, document in lucario.elements.items(): # This is a redundance, but is a good compromise to handle cross-references
            lucario_element = LucarioElement(lucario_id = lucario_information_id, local_document_identifier = local_id)
            sota_information_id = self.find_or_create_lucario_element(lucario_element) # TODO
            mapping[local_id] = sota_information_id
            title = document.file_name
            cite_as = f'{lucario_information_id}:{local_id}'
            try:
                abstract = json.loads(document.description)
                if 'title' in abstract:
                    title = abstract['title']
                if 'cite_as' in abstract:
                    cite_as = abstract['cite_as']
                abstract = DictToHtmlPipeline()(abstract).html
            except Exception as e:
                abstract = document.description
            self.information[sota_information_id].title.versions[-1] = title
            self.information[sota_information_id].abstract.versions[-1] = abstract
            self.information[sota_information_id].reference_as.versions[-1] = cite_as
        return lucario, mapping
        
    def get_lucario(self : 'SOTA', lucario_information_id: int = None) -> LUCARIO:
        if lucario_information_id is None:
            lucario_information_id = self.main_lucario_id
        lucario = self.information[lucario_information_id].get_last_version(self.versions_list(-1))
        assert isinstance(lucario, LUCARIO), "The information is not a LUCARIO element"
        return lucario
    
    def get_leaf_children(self : 'SOTA', information_id : int, version_list : List[int]) -> List[int]:
        last = self.get_last(self.information[information_id].versions, version_list)
        if VersionedInformation.get_class_name(last) == 'Sections':
            return [_ for __ in last.sections for _ in self.get_leaf_children(__, version_list)]
        elif VersionedInformation.get_class_name(last) == 'PlaceHolder':
            return []
        return [information_id]
    
    def find_or_create_lucario_element(self : 'SOTA', lucario_element : LucarioElement) -> int:
        for information_id, information in self.information.items():
            last = self.get_last(information.versions, self.versions_list(-1))
            if VersionedInformation.get_class_name(last) == 'LucarioElement' and last.lucario_id == lucario_element.lucario_id and last.local_document_identifier == lucario_element.local_document_identifier:
                return information_id
        found = self.get_new_id(self.information)
        self.information[found] = VersionedInformation.create_text(
            title = f"Lucario Element {lucario_element.local_document_identifier}",
            contents = lucario_element,
            abstract = f"Lucario Element {lucario_element.local_document_identifier}",
            reference_as = f"{lucario_element.lucario_id}:{lucario_element.local_document_identifier}"
        )
        return found
    
    @classmethod
    def get_empty(cls, lucario: LUCARIO = None) -> 'SOTA':
        return cls(
            title = VersionedText(versions = {1: "New Document"}),
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
                1 : VersionedInformation.create_text(contents = {}, title = 'Body', reference_as = 'Body'),
                2 : VersionedInformation.create_text(
                        contents = LUCARIO.get_new() if lucario is None else lucario,
                        title = 'Knowledge Base',
                        reference_as = 'Knowledge Base'
                    )
            },
            mother_id = 1,
            main_lucario_id = 2,
            styles_sheet = VersionedText(versions = {1: ''}),
            language = Language.en
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
            content = '\n\n'.join([self.build_text(version, subsection_id, focused_information_id = focused_information_id, depth = depth + 1) for subsection_id in latest_content.sections])
        # 4. Get the latest version of the annotations
        if focused_information_id == information_id:
            if info.annotations is None:
                info.annotations = {}
            annotation_ids = get_last(info.active_annotations)
            annotations = annotation_ids if annotation_ids else []
            annotations = [get_last(info.annotations[_].versions) for _ in annotations]
            annotations = [
                {
                    'comment-id': comment_id,
                    'comment_html': comment
                }
                for comment_id, comment in zip(annotation_ids, annotations)
            ]
            annotations = json.dumps(annotations, indent=2)
            desc = self.t('', {'':{
                'en': 'Comments for the focused version',
                'fr': 'Commentaires pour la version focalisée'
            }})
            annotations = f'\n<!-- {desc}:\n{annotations}\n-->\n\n\n'
        
            referencements = get_last(info.referencement_versions)
            referencements_ids = referencements if referencements else []
            referencements = [info.referencements[_] for _ in referencements_ids]
            referencements = { 'referencements': [
                {
                    'refid': refid,
                    'informationid': ref.information_id,
                    'position': ref.detail,
                    'html_contents': ref.analysis
                }
                for refid, ref in zip(referencements_ids, referencements)
            ]}
            referencements = json.dumps(referencements, indent=2)
            desc = self.t('', {'':{
                'en': 'References for the focused version',
                'fr': 'Références pour la version focalisée'
            }})
            referencements = f'\n<!-- {desc}:\n{referencements}\n-->\n\n\n'
            
        else:
            annotations = ''
            referencements = ''
        # 5. Build the text
        start = f'<!-- >>>>>>>>>>>>>>>> {self.t("start")} -->\n' if focused_information_id == information_id else ''
        end = f'<!-- <<<<<<<<<<<<<<<< {self.t("end")} -->\n' if focused_information_id == information_id else ''
        abstract = {'informationid':information_id, 'html_expectations': abstract} if abstract else {}
        abstract = json.dumps(abstract, indent=2) if abstract else ''
        desc = self.t('', {'':{
            'en': 'informationid and Expectations for the focused version',
            'fr': 'informationid et Attendus pour la version focalisée'
        }
        })
        
        abstract = f'\n<!--\n{desc} - {abstract}\n-->\n' if abstract else ''
        title = title if title else ''
        text = f'{start}{referencements}{title}{abstract}{content}{annotations}{end}'
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
            versions_list = self.versions_list(-1)
            structure_references = SOTA.get_last(info.referencement_versions, versions_list) or []
            structure_references = [info.referencements[_] for _ in structure_references]
            structure_references = [{'informationid': ref.information_id, 'position': _.strip()} for ref in structure_references for _ in (ref.detail + ',').split(',')]
            
            # Combine both extracted and structured references, filtering out duplicates and empty positions.
            all_references = structure_references
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
        lucario = self.information[self.main_lucario_id].get_last_version(version_list)
        assert isinstance(lucario, LUCARIO), "The main knowledge base is not a LUCARIO element"
        lucario.update()
        lucario_file_id_to_information_id = {v.file_id: k for k,v in lucario.elements.items()}
        # Now, the important part: the logic of how to build the similarity requests
        if allow_external:
            # in that case, all documents may be used
            file_uuids = [document.file_uuid for document in lucario.elements.values()]
        else:
            # otherwise, only the documents already used may be used
            all_referenced_documents = list(set([_ for i, chunks in referenced_documents.items() for _ in chunks]))
            file_uuids = [lucario.elements[_].file_uuid for _ in all_referenced_documents if _ in lucario.elements]
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