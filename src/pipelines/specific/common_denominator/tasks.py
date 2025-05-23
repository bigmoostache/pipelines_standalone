
from custom_types.PROMPT.type import PROMPT
from custom_types.JSONL.type import JSONL
from custom_types.trees.gap_analysis.type import ResponseType as Tree_Gap_AnalysisResponseType
from typing import List

class Pipeline:
    def __init__(self):
        pass
    def __call__(self,
                doc: dict 
                ) -> List[dict]:
        _res = Tree_Gap_AnalysisResponseType.model_validate(doc)
        tasks = _res.document_denominator.get_tasks()
        return tasks