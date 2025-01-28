from custom_types.JSONL.type import JSONL
import numpy as np
import os

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, concatenated : JSONL) -> JSONL:
        column_order = ['page_start', 'local_index', 'page_end', 'type_of_change', 'importance_of_change', 'CTA', 'changes_description', 'new_formulation', 'old_formulation', 'old_formulation_page_start', 'old_formulation_local_index', 'old_formulation_page_end']

        concatenated.lines.sort(key=lambda x: (int(x['page_start']), (x['local_index'])))
        concatenated.lines = [{k:v.get(k, None) for k in column_order} for v in concatenated.lines]
        return concatenated