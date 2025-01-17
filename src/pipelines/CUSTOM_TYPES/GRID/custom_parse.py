from typing import List
from custom_types.GRID.type import GRID, GRID_SECTION, NOTATION_CRITERIA, POSSIBLE_VALUE
import pandas as pd
from utils.yaml import robust_safe_load
    
class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 text : str) -> GRID:
        s, e = '```yaml\n', '```'
        i0 = text.find(s)
        text = text[i0 + len(s):]
        text = text[:text.find(e)]
        dic = robust_safe_load(text)
        dic = dic['grid']['sections']
        rows = []
        for section in dic:
            name = section['name']
            criteria = []
            for _criteria in section['criteria']:
                criteria.append(NOTATION_CRITERIA(
                    name = _criteria['name'],
                    definition = _criteria['definition'],
                    possible_values = [POSSIBLE_VALUE(value = pv['value'], definition = pv['description']) for pv in _criteria['possible-values']]
                ))
            rows.append(GRID_SECTION(name = name, rows = criteria))
        return GRID(rows = rows)