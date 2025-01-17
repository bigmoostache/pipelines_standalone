from custom_types.GRID.type import GRID, GRID_SECTION, NOTATION_CRITERIA, POSSIBLE_VALUE
from typing import List
import pandas as pd
import numpy as np
import Levenshtein
from pipelines.utils.yaml import robust_safe_load

# If you do not have a Levenshtein library installed, you can use:
# pip install python-Levenshtein
# or you can implement your own. Here we'll demonstrate with python-Levenshtein:

def get_closest_key(query: str, possible_keys: List[str]) -> str:
    """
    Return the key from `possible_keys` that has the minimum Levenshtein distance
    to `query`. 
    """
    best_key = None
    best_distance = float('inf')
    for k in possible_keys:
        distance = Levenshtein.distance(query, k)
        if distance < best_distance:
            best_distance = distance
            best_key = k
    return best_key

class Pipeline:
    def __init__(self):
        pass
    
    def __call__(self, 
                 texts: List[str]) -> dict:
        
        def get_dic(text):
            if '```' in text:
                s, e = '```yaml\n', '```'
                i0 = text.find(s)
                text = text[i0 + len(s):]
                text = text[:text.find(e)]
            return robust_safe_load(text)
        
        # Each item in `texts` presumably contains some YAML with top-level key "evaluation".
        dicts = [get_dic(text)['evaluation'] for text in texts]
        
        final = {}
        total = 0
        
        # We'll assume that the first dictionary's groups and criteria names 
        # serve as the "canonical" reference for iteration:
        for group in dicts[0].keys():
            group_sum = 0

            # Loop over the criteria in the first dictionary for that group:
            for criteria_name in dicts[0][group].keys():
                # For each dictionary, find the locally closest key to `criteria_name`.
                all_values = []
                all_justifications = []
                for d in dicts:
                    local_criteria_name = get_closest_key(criteria_name, d[group].keys())
                    local_value = d[group][local_criteria_name]['value']
                    local_analysis = d[group][local_criteria_name]['analysis']
                    all_values.append(local_value)
                    all_justifications.append((local_value, local_analysis))
                
                # Combine justifications
                justification = "\n ".join(f"{val} - {analysis}" for val, analysis in all_justifications)
                # Compute average (rounded) of the values
                avg_value = int(np.round(np.mean(all_values)))
                
                final[criteria_name] = avg_value
                final[f"{criteria_name} - justification"] = justification
                
                group_sum += avg_value

            final[f'TOTAL - {group}'] = group_sum
            total += group_sum
        
        final['TOTAL'] = total
        return final