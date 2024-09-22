
from custom_types.SOTA.type import SOTA, pipelines, Embedder
from custom_types.JSONL.type import JSONL
from typing import List 

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, sota : SOTA) -> SOTA:
        tasks = []
        versions_list = sota.versions_list(-1)
        active_ids = sota.information[sota.mother_id].get_all_children_ids(sota, sota.mother_id, versions_list)
        active_ids[sota.mother_id] = None
        for bib_id in sota.get_last(sota.bibliography, versions_list):
            active_ids[bib_id] = None
        for k,information in sota.information.items():
            if (k not in active_ids) or (not information.exists_in_stack(versions_list)):
                # ignore inactive information
                continue
            last = SOTA.get_last(information.versions, versions_list)
            if information.get_class_name(last) == 'External'and last.external_db == 'file' and last.external_id.endswith('.pdf'):
                last.external_db = 'file_preprocessed'
                # x
        return sota