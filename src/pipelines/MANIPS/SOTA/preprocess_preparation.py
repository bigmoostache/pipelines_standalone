
from custom_types.SOTA.type import SOTA, pipelines
from typing import List 

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, sota : SOTA) -> List[int]:
        tasks = []
        versions_list = sota.versions_list(-1)
        mother = sota.information[sota.mother_id]
        active_ids = mother.get_all_children_ids(sota, sota.mother_id, versions_list)
        active_ids[sota.mother_id] = None
        for bib_id in sota.get_last(sota.bibliography, versions_list):
            active_ids[bib_id] = None
        for k,information in sota.information.items():
            if (k not in active_ids) or (not information.exists_in_stack(versions_list)):
                # ignore inactive information
                continue
            if not information.external_has_been_processed(versions_list):
                tasks.append(k)
        return tasks