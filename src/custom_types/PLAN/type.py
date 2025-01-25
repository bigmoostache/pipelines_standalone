import json
from typing import List, Union, Literal, Optional
from pydantic import BaseModel, Field
from uuid import uuid4
import re
import markdown2

class Reference(BaseModel):
    document_hash : str = Field(..., description = 'Hash of the document, to avoid storing the same document multiple times')
    reference_id : int = Field(..., description = 'Unique identifier for this reference.')
    citation : str = Field(..., description = 'Citation for the reference')
class Leaf(BaseModel):
    leaf_bullet_points     : List[str] = Field(..., description = 'Bullet points of topics covered. Provide at least 10, or you will fail at this task.')
class Node(BaseModel):
    subsections : List['Plan'] = Field(..., description = 'Subsections of this node')
class Plan(BaseModel):
    section_id             : str = Field(..., description = 'Unique identifier for this plan. It can be anything, as long as it is unique within the document.')
    prefix                 : str = Field(..., description = 'Title prefix, examples: "#", "## 1.", "### 1.1.", etc. It can be letters, numbers, or nothing at all, as long as it is consistent throughout the document. Do not include the title itself.')
    title                  : str = Field(..., description = 'Title for this section. Do not re-specify the prefix.')
    abstract               : str = Field(..., description = 'Short abstract of the sections\'s expected content')
    section_type           : Literal['root', 'node', 'leaf'] = Field(..., description = 'root if root of the whole document, leaf if this section is meant to have subsections, and leaf otherwise.')
    contents               : Union[Leaf, Node] = Field(..., description = 'leaf bullet points if section type = leaf, and subsections if section type = node or root')

    feedback : Optional[str] = Field(None, description = 'Feedback from the reviewer')
    text : Optional[str] = Field(None, description = 'Text of the section')
    references : List[Reference] = Field([], description = 'References for the section')

    def get_leaves(self) -> List['Plan']:
        return [self] if self.section_type == 'leaf' else [__ for _ in self.contents.subsections for __ in _.get_leaves()]
    def aggregate_bullet_points(self, path = ()) -> List[dict]:
        leaves = [_ for _ in self.get_leaves() if _.section_type == 'leaf']
        leaves = [_.dict() for _ in leaves]
        for _ in leaves:
            _['bullets'] = _['contents']['leaf_bullet_points']
        return leaves
    def set_ids_to_unique_uuids(self):
        self.section_id = str(uuid4())
        if self.section_type != 'leaf':
            for _ in self.contents.subsections:
                _.set_ids_to_unique_uuids()

    
    def to_markdown(self, depth = 1):
        if self.section_type == 'leaf':
            r = f"{self.prefix} {self.title}\n{self.text}"
        else:
            children = '\n'.join([_.to_markdown(depth = depth + 1) for _ in self.contents.subsections])
            r = f"{self.prefix} {self.title}\n{children}"
        if depth == 1:
            # Add references
            r+= "\n\n## References"
            for _ in self.references:
                r += f"\n- <ref {_.reference_id}/> __REF_{_.reference_id}__" # This is a placeholder, we will edit the html later
        return r
    
    def to_html(self, template, css):
        markdown = self.to_markdown()
        html = markdown2.markdown(markdown) 
        assert '__HTML__' in template, '__HTML__ not found in the template'
        html = template.replace('__HTML__', html).replace('__CSS__', css)
        
        simple_pattern = r"<ref (\d+) *\/>"
        double_pattern = r"<ref (\d+) *: *(\d+) *\/?>"
        simple_refs = re.findall(simple_pattern, markdown)
        double_refs = re.findall(double_pattern, markdown)
        all_refs = list(set(simple_refs + [_ for _, __ in double_refs]))
        all_plan_refs = [_.reference_id for _ in self.references]
        non_used_refs = set(all_plan_refs) - set(all_refs)
        all_refs_renames = {ref_id: new_ref_id for new_ref_id, ref_id in enumerate(all_refs)}
        
        # Replace references
        def f(i, j, text):
            pattern = rf"<ref {i} *: *{j} *\/>"
            replacement = f"<a href='#ref-{i}?chunk={j}'>[{all_refs_renames[i]}]</a>"
            return re.sub(pattern, replacement, text)
        def g(i, text):
            pattern = rf"<ref {i} *\/>"
            replacement = f"<a href='#ref-{i}'>[{all_refs_renames[i]}]</a>"
            return re.sub(pattern, replacement, text)
        for single_ref in simple_refs:
            html = g(single_ref, html)
        for double_ref in double_refs:
            html = f(double_ref[0], double_ref[1], html)
        
        # Add references
        ref_dict = {_.reference_id: _ for _ in self.references}
        for ref in all_refs:
            html = html.replace(f'__REF_{ref}__', ref_dict[ref].citation)
        for ref in non_used_refs:
            html = html.replace(f'<ref {ref}/>', '')
            html = html.replace(f'__REF_{ref}__', f'[NOT USED] {ref_dict[ref].citation}')
        
        return html
        
class Converter:
    @staticmethod
    def to_bytes(article : Plan) -> bytes:
        return bytes(json.dumps(article.dict()), encoding = 'utf-8')

    @staticmethod
    def from_bytes(b: bytes) -> Plan:
        return Plan.parse_obj(json.loads(b.decode('utf-8')))

    @staticmethod
    def len(article : Plan) -> int:
        return 1
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='plan',
    _class = Plan,
    converter = Converter,
    additional_converters={
        'json': lambda x: x.dict()
        },
    icon='/micons/deepsource.svg'
)