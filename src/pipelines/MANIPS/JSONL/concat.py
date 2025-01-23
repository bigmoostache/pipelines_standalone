from typing import List 
from custom_types.JSONL.type import JSONL

class Pipeline:

    def __init__(self,
                 add_id : bool = False,
                 id_column : str = 'id'):
        self.add_id = add_id
        self.id_column = id_column

    def __call__(self, jsonl : List[JSONL]) -> JSONL:
        if not self.add_id:
            all_lines = [y for x in jsonl for y in x.lines]
        else:
            all_lines = [{**y, self.id_column: i} for i, x in enumerate(jsonl) for y in x.lines]
        return JSONL(all_lines)
