
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
            if (k not in active_ids) or (not information.exists_in_stack(versions_list)):
                # ignore inactive information
                continue
            last_version = information.get_last_version(versions_list)
            version_class_name = information.get_class_name(last_version)
            while information.ai_pipelines_to_run and version_class_name not in pipelines[information.ai_pipelines_to_run[0]]:
                # delete incompatible pipelines
                information.ai_pipelines_to_run.pop(0)
            
            if (not information.ai_pipelines_to_run):
                # no pipeline to run
                continue
            pipeline_name = information.ai_pipelines_to_run[0]
            if pipeline_name == 'Analyse References':
                current_references = sota.get_last(information.referencement_versions, versions_list)
                tasks += [
                    {'task': 'Analyse Reference', 'information' : k, 'referencement_id' : _} 
                    for _ in current_references
                ]
            else:
                tasks.append({'task': pipeline_name, 'information' : k})
        return tasks