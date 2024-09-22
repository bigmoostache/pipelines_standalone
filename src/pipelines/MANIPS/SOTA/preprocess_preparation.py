
from custom_types.SOTA.type import SOTA, pipelines
from typing import List 

class Pipeline:
    def __init__(self,
        only_pdfs : bool = True):
        self.only_pdfs = only_pdfs

    def __call__(
        self, 
        sota : SOTA,
        ) -> List[dict]:
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
            
            last = SOTA.get_last(information.versions, versions_list)
            class_name = information.get_class_name(last)
            if self.only_pdfs and class_name == 'External' and last.external_db == 'file' and last.external_id.endswith('.pdf'):
                tasks.append({
                    'pipeline' : 'pdf',
                    'information_id' : k
                })
            elif not self.only_pdfs and not information.embeddings_are_up_to_date(versions_list):
                tasks.append({
                    'pipeline' : 'embeddings',
                    'information_id' : k
                })
        return tasks