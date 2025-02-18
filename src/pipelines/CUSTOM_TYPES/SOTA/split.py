from custom_types.SOTA.type import SOTA, VersionedInformation
from typing import List
import json
from pipelines.CUSTOM_TYPES.SOTA.call import text_pipelines, sections_pipelines
class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
            sota : SOTA
            ) -> List[dict]:
        res = []
        version_list = sota.versions_list(-1)
        for information_id, info in sota.information.items():
            information = sota.information[information_id]
            last_version_class_name = VersionedInformation.get_class_name(information.get_last_version(version_list))
            while info.ai_pipelines_to_run:
                pipeline = json.loads(info.ai_pipelines_to_run.pop(0))
                pipeline_name = pipeline['name']
                if last_version_class_name == 'str' and pipeline_name in text_pipelines:
                    res.append({
                        'information_id': information_id,
                        **pipeline
                    })
                    break
                elif last_version_class_name == 'Sections' and pipeline_name in sections_pipelines:
                    res.append({
                        'information_id': information_id,
                        **pipeline
                    })
                    break
        return res