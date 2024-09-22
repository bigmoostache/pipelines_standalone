
from custom_types.SOTA.type import SOTA, pipelines
from custom_types.JSONL.type import JSONL
from typing import List 

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, sota : SOTA, task: dict) -> JSONL:
        res = []
        information_id = task.get('information_id', None)
        information = sota.information.get(information_id, None)
        if information is None:
            raise ValueError("information_id is corrupted: informaiton not found")
        versions_list = sota.versions_list(-1)
        
        abstract = SOTA.get_last(information.abstract.versions, versions_list)
        content = SOTA.get_last(information.versions, versions_list)
        if abstract and abstract.strip():
            res.append({
                'information_id' : information_id,
                'section_id': 'abstract',
                'context': 'Section abstract and attendus',
                'content': abstract
            })
        if content:
            content = str(content).strip()
            if content:
                res.append({
                    'information_id' : information_id,
                    'section_id': 'content',
                    'context': 'Section content',
                    'content': content
                })
        return JSONL(lines=res)