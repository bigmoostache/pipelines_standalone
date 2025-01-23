import json
import base64
from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field

class Leaf(BaseModel):
    leaf_bullet_points     : List[str] = Field(..., description = 'Bullet points of topics covered. Provide at least 10, or you will fail at this task.')
class Node(BaseModel):
    subsections : List['Plan'] = Field(..., description = 'Subsections of this node')
class Plan(BaseModel):
    prefix                 : str = Field(..., description = 'Title prefix, which has to follow one of the following regex expression: Regex(#) (for root), Regex(## [A-Z]\.) (for depth = 1, example: ## A.), or Regex(### [A-Z]\.\d+\.)" (depth = 2, example: ### A.1.) or Regex(#### [A-Z]\.\d+\.[a-z]\.) (depth = 3. example: #### A.1.a.) or Regex(##### [A-Z]\.\d+\.[a-z]\.\d+\)) (depth = 4, example: #### A.1.a.1)), etc. If you fail at following this exact pattern, you will fail at this task and receive a grade of zero.')
    title                  : str = Field(..., description = 'Title for this section. Do not re-specify the prefix.')
    abstract               : str = Field(..., description = 'Short abstract of the sections\'s expected content')
    section_type           : Literal['root', 'node', 'leaf'] = Field(..., description = 'root if root of the whole document, leaf if this section is meant to have subsections, and leaf otherwise.')
    contents               : Union[Leaf, Node] = Field(..., description = 'leaf bullet points if section type = leaf, and subsections if section type = node or root')


class Converter:
    @staticmethod
    def to_bytes(article : Plan) -> bytes:
        return bytes(json.dumps(article.to_dict()), encoding = 'utf-8')

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