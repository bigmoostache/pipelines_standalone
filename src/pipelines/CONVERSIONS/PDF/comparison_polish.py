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
        # increase all page numbers by 1 to match the page numbers in the pdf
        for line in concatenated.lines:
            line['page_start'] = str(int(line['page_start']) + 1)
            line['page_end'] = str(int(line['page_end']) + 1)
            line['old_formulation_page_start'] = str(int(line['old_formulation_page_start']) + 1)
            line['old_formulation_page_end'] = str(int(line['old_formulation_page_end']) + 1)
        # rename columns to more human-readable names
        renames = {
            'page_start': 'Page Start',
            'local_index': 'Chunk in Page',
            'page_end': 'Page End',
            'type_of_change': 'Type of Change',
            'importance_of_change': 'Importance of Change',
            'CTA': 'CTA',
            'changes_description': 'Changes Description',
            'new_formulation': 'New Formulation',
            'old_formulation': 'Old Formulation',
            'old_formulation_page_start': 'Old Formulation Page Start',
            'old_formulation_local_index': 'Old Formulation Chunk in Page',
            'old_formulation_page_end': 'Old Formulation Page End'
        }
        concatenated.lines = [{renames[k]: v for k, v in line.items()} for line in concatenated.lines]
        return concatenated