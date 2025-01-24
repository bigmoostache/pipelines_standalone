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
        return JSONL(lines = p.aggregate_bullet_points())