from typing import List
from custom_types.XLSX.type import XLSX
import pandas as pd

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 dicts : List[dict]
                 ) -> XLSX:
        def process(name, dics : List[dict], parent_df = None, parent_id_col = None, sheet_number : int = 1):
            my_id_column = f'{name}_id'
            sheet_keys = list(set([k for dic in dics for k,v in dic.items() if isinstance(v, list)]))
            # Check if parent_id_col is in all dicts
            if parent_df is not None:
                for i,d in enumerate(dics):
                    assert parent_id_col in d, f'parent_id_col {parent_id_col} not in dict {d}'
            # Add id column to all dicts and subdicts in order to allow merge in recursive calls
            if len(sheet_keys) > 0:
                for i,d in enumerate(dics):
                    d[my_id_column] = i
                    for sheet in sheet_keys:
                        for _ in d[sheet]:
                            _[my_id_column] = i
            # Compute main_df: keys that are not lists
            direct_keys = list(set([k for dic in dics for k,v in dic.items() if not isinstance(v, list)]))
            # Check that intersection between direct_keys and sheet_keys is empty
            intersection = set(direct_keys).intersection(sheet_keys)
            assert len(intersection) == 0, f'intersection between direct_keys and sheet_keys is not empty: {intersection}'
            # Check that parent_id_col and my_id_column are direct_keys
            if parent_df is not None:
                assert parent_id_col in direct_keys, f'parent_id_col {parent_id_col} not in direct_keys {direct_keys}'
            if len(sheet_keys) > 0:
                assert my_id_column in direct_keys, f'my_id_column {my_id_column} not in direct_keys {direct_keys}'
            # Build main_df
            main_df = pd.DataFrame([{k:v for k,v in d.items() if k in direct_keys} for d in dics])
            # Merge with parent_df if it exists
            if parent_df is not None:
                main_df = parent_df.merge(main_df, left_on=parent_id_col, right_on=parent_id_col, how='left', suffixes=('', f'_{name}'))
            # Create the result dictionary
            res = {f'{sheet_number}_{name}' : main_df}
            sheet_number += 1
            # Recursive call for all sheet_keys
            for k in sheet_keys:
                lines = [_ for __ in dics for _ in __[k]]
                sheet_number, sheets = process(k, lines, main_df, my_id_column, sheet_number)
                res = {**res, **sheets}
            return sheet_number, res
        return XLSX(sheets = process('Sheet1', dicts, parent_df = None, id_col = None)[1])