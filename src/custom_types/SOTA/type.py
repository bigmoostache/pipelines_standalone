from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Dict, Optional, Tuple, Union, Literal
from datetime import datetime
import json

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
    previous_version_id : int | None = Field(..., description="ID of parent version. If None, then initializes a tree.")

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
class VersionedInformation(BaseModel):
    # Actual Content
    
    class Paragraphs(BaseModel):
        paragraphs : List[FormatedText]
    class PlaceHolder(BaseModel):
        pass
    class Sections(BaseModel):
        enumeration : Literal["Numbers enumeration", "Latin enumeration", "Lowercase letters enumeration", "Capital letters enumeration", "Concatenation"] = Field(..., description = "Wheter to enumerate or itemize")
        sections    : List[Tuple[bool, int]] = Field(..., description = "Tuple[Section Name, Whether to show this section name, information_id]")
    class Image(BaseModel):
        url         : str                 = Field(..., description = "Image public url")
        label       : str                 = Field(..., description = "Image label")
    class Table(BaseModel):
        csv             : str             = Field(..., description = "utf-8 encoded csv, with columns.")
        column_groups   : List[str]       = Field(..., description = "List of column names to aggregated rows by, in the right order. Can be empty.")
        column_hierarcy : dict            = Field(..., description = "Tree. Each node is a string. Leafs are column names. Will aggregate columns according to that tree. Non found columns will be isolated.")
    class External(BaseModel):
        external_db : str                 = Field(..., description = "Database, provider, api, whatever. Must match an implemented algorithm.")
        external_id : str | int           = Field(..., description = "External identifier. May be anything. Unlike the Sections model, conceptually, the information here is not just the id, it is also the information behind the underlying entity.")

    versions : Dict[int,  PlaceHolder | Sections | Image | Table | External | str | Paragraphs | FormatedText] = Field(..., description = "Content of the versioned information. The key is the version id.")

    # TODO: versioned text for str entries
    class Referencement(BaseModel):
        information_id : int              = Field(..., description = "information_id")
        detail         : str              = Field(..., max_length = 20, description = "Very short detail about where exactly in the information to look (eg: the page number, t)")
        analysis       : str              = Field(..., description = "Analysis of the reference w.r.t. this information.")
        pertinence     : float
        
    referencements : Dict[int, Referencement]     = Field(..., description = "local_referencement_id -> Referencement")
    referencement_versions : Dict[int, List[int]] = Field(..., description = "version_id -> List[local_annotation_id]")

    title    : VersionedText
    abstract : VersionedText
    reference_as : VersionedText = Field(..., description = "If you reference this section, this reference_as string will appear")
    
    annotations : Dict[int, VersionedText]    = Field(..., description = "local_annotation_id -> Annotation")
    active_annotations : Dict[int, List[int]] = Field(..., description = "version_id -> List[local_annotation_id]")


class Document(BaseModel):
    title              : VersionedText      = Field(..., description = "Document title")
    drop_url           : str
    
    versions           : Dict[int, Version] = Field(..., description = "version_id -> Version")
    current_version_id : int                = Field(..., description = "version_id of the currently featured version.")
    
    authors            : Dict[int, Author]  = Field(..., description = "author_id -> Author")
    signatures         : List[SignHere]     = Field(..., description = "A list of signatures related to the Document.")
    keywords           : Dict[int, Keyword] = Field(..., description = "A list of keywords used globally in the Document.")

    information        : Dict[int, VersionedInformation] = Field(..., description = "information_id -> VersionedInformation")
    mother_id          : int                  = Field(..., description = "Master information for the rendering")
    bibliography       : Dict[int, List[int]] = Field(..., description = "version_id -> List[information_id]")

class Converter:
    @staticmethod
    def to_bytes(doc : Document) -> bytes:
        return doc.model_dump_json(indent=2).encode('utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> Document:
        return Document.parse_obj(json.loads(b.decode('utf-8')))
    @staticmethod
    def str_preview(doc: Document) -> str:
        return doc.model_dump_json(indent=2)[:10000]
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='sota',
    _class = Document,
    converter = Converter,
    visualiser = "https://sota.croquo.com"
)
