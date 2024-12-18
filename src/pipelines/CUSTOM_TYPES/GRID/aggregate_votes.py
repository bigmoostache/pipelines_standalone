from typing import List
from custom_types.GRID.type import GRID, GRID_SECTION, NOTATION_CRITERIA, POSSIBLE_VALUE
import pandas as pd
import yaml
import numpy as np

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 texts : List[str]) -> dict:
        def get_dic(text):
            if '```' in text:
                s, e = '```yaml\n', '```'
                i0 = text.find(s)
                text = text[i0 + len(s):]
                text = text[:text.find(e)]
            return yaml.safe_load(text)
        dicts = [get_dic(_)['evaluation'] for _ in texts]
        final = {}
        total = 0
        for group in dicts[0].keys():
            sum = 0
            for criteria_name in dicts[0][group].keys():
                values = [_[group][criteria_name]['value'] for _ in dicts]
                tuples = [(_[group][criteria_name]['value'], _[group][criteria_name]['analysis']) for _ in dicts]
                justification = '\n '.join(f'{k} - {v}' for k,v in tuples)
                final[criteria_name] = int(np.round(np.mean(values)))
                sum += final[criteria_name]
                final[f'{criteria_name} - justification'] = justification
            final[f'TOTAL - {group}'] = sum
            total += sum
        final['TOTAL'] = total
        return final