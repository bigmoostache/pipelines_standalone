import openai
from typing import List
import os 
from custom_types.JSONL.type import JSONL
from custom_types.PLAN.type import Plan

class Pipeline:
    def __init__(self, 
                 ):
        pass
    
    def __call__(self, 
            p : Plan
            ) -> JSONL:
        def aggregate_bullet_points(self, path = ()) -> List[str]:
            return [{'bullets':[_ for _ in self.contents.leaf_bullet_points], 'path':path}] if self.section_type == 'leaf' else [__ for i,_ in enumerate(self.contents.subsections) for __ in _.aggregate_bullet_points(path + (i,))]
        return JSONL(lines = aggregate_bullet_points(p))