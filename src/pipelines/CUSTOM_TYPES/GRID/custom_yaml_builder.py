from custom_types.GRID.type import GRID
import re

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 grid : GRID) -> str:
        def transform(s): return re.sub(r'[^a-z0-9\s]', '', s.lower()).replace(' ', '-')
        def remove_line_returns(s): return s.replace('\n', '').replace('\r', '')
        yaml = 'evaluation:'
        for row in grid.rows:
            yaml += f'\n  {transform(row.name)}:'
            for criteria in row.rows:
                last = criteria.possible_values[-1].value
                vals = ', '.join([str(_.value) for _ in criteria.possible_values][:-1]) + f' or {last}'
                value_defs = '\n      # '.join(['']+[_.definition for _ in criteria.possible_values])
                yaml += f'\n    {transform(criteria.name)}: \
                \n      # {remove_line_returns(criteria.definition)}{value_defs}\
                \n      analysis: <string>\
                \n      value: <integer, {vals}>'
        return yaml