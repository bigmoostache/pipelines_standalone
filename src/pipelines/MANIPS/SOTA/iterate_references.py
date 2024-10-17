
from custom_types.SOTA.type import SOTA, pipelines
from typing import List 

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, sota : SOTA) -> List[dict]:
        tasks = []
        versions_list = sota.versions_list(-1)
        mother = sota.information[sota.mother_id]
        active_ids = mother.get_all_children_ids(sota, sota.mother_id, versions_list)
        active_ids[sota.mother_id] = None
        for k,information in sota.information.items():
            if len(information.ai_pipelines_to_run) == 0:
                continue
            tasks.append(
                {'task': 'Iterate References', 'information' : k} 
            )
        return tasks