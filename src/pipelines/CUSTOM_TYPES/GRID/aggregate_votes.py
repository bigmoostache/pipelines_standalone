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
        for group in dicts[0].keys():
            for criteria_name in dicts[0][group].keys():
                values = [_[group][criteria_name]['value'] for _ in dicts]
                tuples = [(_[group][criteria_name]['value'], _[group][criteria_name]['analysis']) for _ in dicts]
                justification = '\n '.join(f'{k} - {v}' for k,v in tuples)
                final[criteria_name] = np.mean(values)
                final[f'{criteria_name} - justification'] = justification
        return final