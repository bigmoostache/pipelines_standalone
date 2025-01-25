from custom_types.PLAN.type import Plan, Reference
from custom_types.JSONL.type import JSONL
from pipelines.utils.simplify import simplify

class Pipeline:
    def __init__(self, 
                 ):
        pass
    
    def __call__(self, 
            p : Plan,
            knowledge: JSONL
            ) -> Plan:
        refs = {}
        for _ in knowledge.lines:
            if _['document_id'] not in refs:
                refs[_['document_id']] = _['reference']
        for k,v in refs.items():
            p.references.append(Reference(document_hash=str(k), reference_id=k, citation=v))
        return p