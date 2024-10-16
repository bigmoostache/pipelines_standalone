
from custom_types.SOTA.type import SOTA, pipelines
from custom_types.JSONL.type import JSONL
from typing import List 
import requests

class Pipeline:
    def __init__(
        self,
        k : int = 10,
        max_per_information : int = 0,
        file_ids : List[int] = [],
        ):
        self.k = k
        self.max_per_information = max_per_information
        self.file_ids = file_ids

    def __call__(self, sota : SOTA, task: dict) -> JSONL:

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        json_data = {
            'project_id': '1728993524.7400432.9001c424-7692-435f-8592-e00abe3a51be',
            'query_text': 'Of the use of mathematics and computer science in the field of osteoporosis',
            'k': self.k,
            'file_ids': self.file_ids,
            'max_per_information': 0,
        }

        response = requests.post(f'{sota.drop_url}/top_k', headers=headers, json=json_data)
        
        
        res = []
        information_id = task.get('information_id', None)
        information = sota.information.get(information_id, None)
        if information is None:
            raise ValueError("information_id is corrupted: informaiton not found")
        versions_list = sota.versions_list(-1)
        content = SOTA.get_last(information.versions, versions_list)
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