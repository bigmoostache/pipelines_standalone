from custom_types.GRID.type import GRID, GRID_SECTION, NOTATION_CRITERIA, POSSIBLE_VALUE
from typing import List
import pandas as pd
import numpy as np
from pipelines.utils.yaml import robust_safe_load

class Pipeline:
    def __init__(self):
        pass
    
    def __call__(self, 
                 dicts: List[dict]) -> dict:
        
        final = {}
        total = 0
        total_non_rounded = 0
        total_median = 0
        
        # We'll assume that the first dictionary's groups and criteria names 
        # serve as the "canonical" reference for iteration:
        for group in dicts[0].keys():
            group_sum = 0
            group_sum_non_rounded = 0
            group_sum_median = 0

            # Loop over the criteria in the first dictionary for that group:
            for criteria_name in dicts[0][group].keys():
                # For each dictionary, find the locally closest key to `criteria_name`.
                all_values = []
                all_justifications = []
                for d in dicts:
                    local_value = d[group][criteria_name][f'{criteria_name}_value']
                    local_analysis = d[group][criteria_name][f'{criteria_name}_analysis']
                    all_values.append(local_value)
                    all_justifications.append((local_value, local_analysis))
                
                # Combine justifications
                justification = "\n ".join(f"{val} - {analysis}" for val, analysis in all_justifications)
                # Compute average (rounded) of the values
                avg_value_rounded = int(np.round(np.mean(all_values)))
                avg_value_non_rounded = np.mean(all_values)
                median_value = np.median(all_values)
                
                final[criteria_name] = avg_value_rounded
                final[f"{criteria_name} - non-rounded value"] = avg_value_non_rounded
                final[f"{criteria_name} - median value"] = median_value
                final[f"{criteria_name} - justification"] = justification
                
                group_sum += avg_value
                group_sum_non_rounded += avg_value_non_rounded
                group_sum_median += median_value

            final[f'TOTAL - {group}'] = group_sum
            final[f'TOTAL - {group} - non-rounded'] = group_sum_non_rounded
            final[f'TOTAL - {group} - median'] = group_sum_median
            
            total += group_sum
            total_non_rounded += group_sum_non_rounded
            total_median += group_sum_median
        
        final['TOTAL'] = total
        final['TOTAL - non-rounded'] = total_non_rounded
        final['TOTAL - median'] = total_median
        return final