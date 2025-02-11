from custom_types.SOTA.type import SOTA, VersionedInformation, VersionedText, Sections

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from openai import OpenAI
import os

class Node(BaseModel):
    contents_type : Literal['Node', 'Leaf Text', 'Leaf Image', 'Leaf Table'] = Field(..., description = "Paragraph, Image and Table are leaves, while Secion is node containing nested information.")
    title : str = Field(..., description = "Section title")
    substance : List[str] = Field(..., description = "Enumerate what should be discussed here. Be very precise and exhaustive.")
    form : List[str] = Field(..., description = "Describe what is expected of the form of this section: provide a list of quality criteria independent of the content itself.")
    contents : Optional[List['Node']] = Field(..., description = "Only if contents_type = Section")

def openai(prompt, api_key):
    client = OpenAI(api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Create the document structure as requested"},
            {"role": "user", "content": prompt},
        ],
        response_format=Node,
    )
    return completion.choices[0].message.parsed

def build_abstract(node):
    substance = '\n- '.join(node.substance)
    form = '\n- '.join(node.form)
    return f'Substance:\n- {substance}\n\nForm:\n- {form}'
def build_sota(sota, node, i = -1, use_information_id = None, base_reference = ''):
    i += 1
    abstract = build_abstract(node)
    if node.contents is not None:
        children = []
        enumeration = 1
        for subnode in node.contents:
            i, _information_id = build_sota(sota, subnode, i,base_reference = f'{base_reference}{enumeration}.')
            enumeration += 1
            children.append((True, _information_id))
        versioned_info = VersionedInformation.create_text(contents = Sections(enumeration='Numbers enumeration', sections = children), title = node.title, abstract = abstract, reference_as = base_reference)
    elif node.contents_type in {'Leaf Text', 'Node', 'Leaf Table'}:
        versioned_info = VersionedInformation.create_text(title = node.title, abstract = abstract, reference_as = base_reference)
    elif node.contents_type == 'Leaf Image':
        versioned_info = VersionedInformation.create_text(contents = VersionedInformation.Image(url = '', label = node.title), title = node.title, abstract = abstract, reference_as = base_reference)
    else:
        raise
    information_id = use_information_id if use_information_id is not None else SOTA.get_new_id(sota.information)
    sota.information[information_id] = versioned_info
    return i, information_id

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self):
        pass 
    def __call__(self, text : str) -> SOTA:
        root = openai(text, os.environ.get("openai_api_key"))
        sota = SOTA.get_empty()
        build_sota(sota, root, use_information_id = 1)
        sota.title = VersionedText(versions={-1:root.title})
        return sota