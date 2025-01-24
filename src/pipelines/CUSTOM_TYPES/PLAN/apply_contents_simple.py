from typing import List
from custom_types.PLAN.type import Plan
from pipelines.utils.simplify import simplify

class Pipeline:
    def __init__(self, 
                 ):
        pass
    
    def __call__(self, 
            p : Plan,
            text : str
            ) -> Plan:
        lines = text.split('\n')
        if simplify(lines[0]) == simplify(p.title):
            # remove the title from the text
            p.text = '\n'.join(lines[1:])
        else:
            p.text = text
        return p