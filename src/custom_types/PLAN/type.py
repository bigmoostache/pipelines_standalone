import json
from typing import List, Union, Literal, Optional
from pydantic import BaseModel, Field
from custom_types.LUCARIO.type import LUCARIO
from uuid import uuid4
import re
import markdown2

class Reference(BaseModel):
    document_hash : str = Field(..., description = 'Hash of the document, to avoid storing the same document multiple times')
    reference_id : int = Field(..., description = 'Unique identifier for this reference.')
    citation : str = Field(..., description = 'Citation for the reference')
    external_id : Optional[str] = Field(None, description = 'External identifier for the reference, e.g. DOI')
class Leaf(BaseModel):
    leaf_bullet_points     : List[str] = Field(..., description = 'Bullet points of topics covered. Provide at least 10, or you will fail at this task.')
    target_number_of_words : Optional[int] = Field(250, description = 'Target number of words for the section.')
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
    lucario: Optional[LUCARIO] = Field(None, description = 'Knowledge based')

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
            r+= "\n\n## References\n"
            if self.lucario is not None:
                for ref_id, element in self.lucario.elements.items():
                    r += f"\n- <ref {ref_id}/> <REF_{ref_id}>"
            else:
                for i, ref in enumerate(self.references):
                    r += f"\n- <ref {i}/> <REF_{i}>"
        return r
    
    
    def to_html(self, template, css):
        self.lucario.update()
        markdown = self.to_markdown()
        html = markdown2.markdown(markdown) 
        assert '__HTML__' in template, '__HTML__ not found in the template'
        html = template.replace('__HTML__', html).replace('__CSS__', css)
        
        simple_pattern = r"<ref (\d+) *\/>"
        double_pattern = r"<ref (\d+) *: *(\d+) *\/?>"
        simple_refs = re.findall(simple_pattern, markdown)
        simple_refs = [int(_) for _ in simple_refs]
        double_refs = re.findall(double_pattern, markdown)
        double_refs = [(int(_), int(__)) for _, __ in double_refs]
        all_refs = list(set(simple_refs + [_ for _, __ in double_refs]))
        all_plan_refs = [_.reference_id for _ in self.references]
        non_used_refs = set(all_plan_refs) - set(all_refs)
        all_refs_renames = {ref_id: new_ref_id+1 for new_ref_id, ref_id in enumerate(all_refs)}
        
        # Replace references
        def f(i, j, text):
            pattern = rf"<ref {i} *: *{j} *\/>"
            replacement = f"<a href='#ref-{i}'>[{all_refs_renames[i]}]</a>"
            return re.sub(pattern, replacement, text)
        def g(i, text):
            pattern = rf"<ref {i} *\/> <REF"
            replacement = "<REF"
            text = re.sub(pattern, replacement, text)
            pattern = rf"<ref {i} *\/>"
            replacement = f"<a href='#ref-{i}'>[{all_refs_renames[i]}]</a>"
            return re.sub(pattern, replacement, text)
        for single_ref in simple_refs:
            html = g(single_ref, html)
        for double_ref in double_refs:
            html = f(double_ref[0], double_ref[1], html)
        
        # Add references
        def get_citation(ref_id):
            try:
                x = self.lucario.elements[ref_id].description
                x = json.loads(x)
                return x['reference']
            except:
                try:
                    x = self.lucario.elements[ref_id].file_uuid
                    return f'<a href="{self.lucario.url}/files?file={x}">Access file</a>'
                except:
                    return 'No reference available'
        def get_uuid(ref_id):
            return self.lucario.elements[ref_id].file_uuid
        for ref in all_refs:
            html = html.replace(f'<REF_{ref}>', f'<a href="{self.lucario.url}/files?file={get_uuid(ref)}">[{ref}]</a> <span id="ref-{ref}">{get_citation(ref)}</span>')
        for ref in non_used_refs:
            html = html.replace(f'<ref {ref}/>', '')
            html = html.replace(f'__REF_{ref}__', f'[NOT USED] {get_citation(ref)}')
        return html
        
class Converter:
    @staticmethod
    def to_bytes(article : Plan) -> bytes:
        def custom_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()  # Convert datetime to ISO formatted string
            raise TypeError(f"Type {type(obj).__name__} is not JSON serializable")
        return bytes(json.dumps(article.dict(), default=custom_serializer), encoding = 'utf-8')

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
    icon='/micons/deepsource.svg',
    visualiser = "https://vis.deepdocs.net/plan"
)