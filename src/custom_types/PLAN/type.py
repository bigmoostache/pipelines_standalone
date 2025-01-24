import json
import base64
from typing import List, Union, Literal
from pydantic import BaseModel, Field

class Leaf(BaseModel):
    leaf_bullet_points     : List[str] = Field(..., description = 'Bullet points of topics covered. Provide at least 10, or you will fail at this task.')
class Node(BaseModel):
    subsections : List['Plan'] = Field(..., description = 'Subsections of this node')
class Plan(BaseModel):
    prefix                 : str = Field(..., description = 'Title prefix, examples: "#", "## 1.", "### 1.1.", etc. It can be letters, numbers, or nothing at all, as long as it is consistent throughout the document. Do not include the title itself.')
    title                  : str = Field(..., description = 'Title for this section. Do not re-specify the prefix.')
    abstract               : str = Field(..., description = 'Short abstract of the sections\'s expected content')
    section_type           : Literal['root', 'node', 'leaf'] = Field(..., description = 'root if root of the whole document, leaf if this section is meant to have subsections, and leaf otherwise.')
    contents               : Union[Leaf, Node] = Field(..., description = 'leaf bullet points if section type = leaf, and subsections if section type = node or root')

    def aggregate_bullet_points(self, path = ()) -> List[str]:
        return [{'bullets':[_ for _ in self.contents.leaf_bullet_points], 'path':path}] if self.section_type == 'leaf' else [__ for i,_ in enumerate(self.contents.subsections) for __ in _.aggregate_bullet_points(path + (i,))]
    
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
    icon='/micons/deepsource.svg'
)