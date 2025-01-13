from typing import List
from custom_types.GRID.type import GRID, GRID_SECTION, NOTATION_CRITERIA, POSSIBLE_VALUE
import pandas as pd
import yaml

def robust_safe_load(yaml_text):
    """
    Attempt to load YAML text in a 'robust' manner:
      1. Try normal yaml.safe_load.
      2. If that fails, do a naive fix for lines that appear to have unquoted colons
         in the value part, then re-try loading.

    Returns:
        Parsed Python object (dict, list, etc.) if successful, otherwise raises.
    """
    try:
        # First attempt: just parse directly
        return yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        fixed_lines = []
        for line in yaml_text.splitlines():

            match = re.match(r'^(\s*(?:- )?[^:]+:\s)(.*:.*)$', line)
            if match:
                prefix = match.group(1)  # e.g. "key: " or "- name: "
                rest   = match.group(2)  # e.g. "Domain 1 : More text"
                
                # Wrap the rest in quotes (escape existing quotes if any)
                rest_escaped = rest.replace('"', '\\"')
                new_line = f'{prefix}"{rest_escaped}"'
                fixed_lines.append(new_line)
            else:
                # No suspicious pattern found; leave line alone
                fixed_lines.append(line)

        # Now try parsing again with the 'fixed' text
        fixed_text = "\n".join(fixed_lines)
        return yaml.safe_load(fixed_text)
    
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