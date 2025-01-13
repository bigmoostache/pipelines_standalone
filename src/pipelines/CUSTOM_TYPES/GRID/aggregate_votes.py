from typing import List
from custom_types.GRID.type import GRID, GRID_SECTION, NOTATION_CRITERIA, POSSIBLE_VALUE
import pandas as pd
import yaml
import numpy as np

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
                 texts : List[str]) -> dict:
        def get_dic(text):
            if '```' in text:
                s, e = '```yaml\n', '```'
                i0 = text.find(s)
                text = text[i0 + len(s):]
                text = text[:text.find(e)]
            return robust_safe_load(text)
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