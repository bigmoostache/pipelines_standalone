import openai
from typing import List
import os 
from custom_types.PROMPT.type import PROMPT
from custom_types.PLAN.type import Plan
from pipelines.LLMS.v3.client import Providers
from typing import List, Union, Literal
from pydantic import BaseModel, Field
from pipelines.LLMS.v3.structured import Pipeline as StructuredPipeline

class Leaf(BaseModel):
    leaf_bullet_points     : List[str] = Field(..., description = 'Bullet points of topics covered. Provide at least 10, or you will fail at this task.')
class Node(BaseModel):
    subsections : List['PlanForLLM'] = Field(..., description = 'Subsections of this node')
class PlanForLLM(BaseModel):
    section_id             : str = Field(..., description = 'Unique identifier for this plan. It can be anything, as long as it is unique within the document.')
    prefix                 : str = Field(..., description = 'Title prefix, examples: "#", "## 1.", "### 1.1.", etc. It can be letters, numbers, or nothing at all, as long as it is consistent throughout the document. Do not include the title itself.')
    title                  : str = Field(..., description = 'Title for this section. Do not re-specify the prefix.')
    abstract               : str = Field(..., description = 'Short abstract of the sections\'s expected content')
    section_type           : Literal['root', 'node', 'leaf'] = Field(..., description = 'root if root of the whole document, leaf if this section is meant to have subsections, and leaf otherwise.')
    contents               : Union[Leaf, Node] = Field(..., description = 'leaf bullet points if section type = leaf, and subsections if section type = node or root')

    def to_plan(self):
        return Plan.parse_obj(self.dict())
    
class Pipeline:
    def __init__(self, 
                 model : str = "gpt-4o", 
                 provider: Providers = "openai",
                 base_url : str = "https://api.openai.com/v1",
                 temperature : float = 1, 
                 top_p : float = 1
                 ):
        self.pipeline = lambda p : StructuredPipeline(
            provider=provider, 
            model=model
        )(p, PlanForLLM).to_plan()
        
    def __call__(self, 
            p : PROMPT
            ) -> Plan:
        p.truncate()
        return self.pipeline(p)