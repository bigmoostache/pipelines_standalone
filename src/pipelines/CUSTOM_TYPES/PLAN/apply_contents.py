from typing import List
from custom_types.PLAN.type import Plan

class Pipeline:
    def __init__(self, 
                 ):
        pass
    
    def __call__(self, 
            p : Plan,
            sections : List[Plan]
            ) -> Plan:
        sections = {_.section_id: _ for _ in sections}
        def process(_plan: Plan):
            if _plan.section_type != 'leaf':
                for _ in _plan.contents.subsections:
                    process(_)
            else:
                if _plan.section_id in sections:
                    _plan.text = sections[_plan.section_id].text
        process(p)
        return p