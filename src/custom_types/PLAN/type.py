import json
import base64
from typing import List, Union, Literal
from pydantic import BaseModel, Field
from uuid import uuid4

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

    def get_leaves(self) -> List['Plan']:
        return [self] if self.section_type == 'leaf' else [__ for _ in self.contents.subsections for __ in _.get_leaves()]
    def aggregate_bullet_points(self, path = ()) -> List[str]:
        leaves = self.get_leaves()
        leaves = [_ for _ in leaves if _.section_type == 'leaf']
        leaves = [_.dict() for _ in leaves]
        for _ in leaves:
            _['bullets'] = _['contents']['leaf_bullet_points']
        return leaves
    def set_ids_to_unique_uuids(self) -> 'Plan':
        self.section_id = str(uuid4())
        if self.section_type == 'leaf':
            return
        for i, _ in enumerate(self.contents.subsections):
            _.set_ids_to_unique_uuids()
        return self
    
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