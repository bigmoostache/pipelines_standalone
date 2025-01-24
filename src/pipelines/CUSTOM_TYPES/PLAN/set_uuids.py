from typing import List
from custom_types.JSONL.type import JSONL
from custom_types.PLAN.type import Plan

class Pipeline:
    def __init__(self, 
                 ):
        pass
    
    def __call__(self, 
            p : Plan
            ) -> Plan:
        p.set_ids_to_unique_uuids()
        return p