from typing import List
from custom_types.XLSX.type import XLSX
import pandas as pd
from custom_types.XTRK.type import DataStructure

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 dicts : List[dict],
                 grid: DataStructure
                 ) -> XLSX:
        def process(name, dics : List[dict], parent_df = None, parent_id_col = None, sheet_number : int = 1, sub_grid: DataStructure = grid):
            sheet_keys = [f.object_name for f in sub_grid.fields if hasattr(f.object_type, 'object_list')]
            # Check if parent_id_col is in all dicts
            if parent_df is not None:
                for i,d in enumerate(dics):
                    assert parent_id_col in d, f'parent_id_col {parent_id_col} not in dict {d}'
            # Add id column to all dicts and subdicts in order to allow merge in recursive calls
            my_id_column = f'{name}_id'
            if len(sheet_keys) > 0:
                for i,d in enumerate(dics):
                    d[my_id_column] = i
                    for sheet in sheet_keys:
                        for _ in d[sheet]:
                            _[my_id_column] = i
            # Compute main_df: keys that are not lists
            direct_keys = [f.object_name for f in sub_grid.fields if not hasattr(f.object_type, 'object_list')]

            # If we have a parent_df, we must ensure parent_id_col is present in main_df
            if parent_df is not None and parent_id_col not in direct_keys:
                direct_keys.append(parent_id_col)

            # If we have sheet_keys, we have a my_id_column that must also be present
            if len(sheet_keys) > 0:
                if my_id_column not in direct_keys:
                    direct_keys.append(my_id_column)

            # Now perform the assertions
            if parent_df is not None:
                assert parent_id_col in direct_keys, f'parent_id_col {parent_id_col} not in direct_keys {direct_keys}'
            if len(sheet_keys) > 0:
                my_id_column = f'{name}_id'
                assert my_id_column in direct_keys, f'my_id_column {my_id_column} not in direct_keys {direct_keys}'

            # Build main_df
            if len(dics) == 0:
                # If there are no dicts, create an empty DataFrame. Since we must merge on parent_id_col,
                # ensure the DataFrame has at least that column (if parent_df is not None).
                if parent_df is not None:
                    main_df = pd.DataFrame(columns=[parent_id_col])
                else:
                    main_df = pd.DataFrame()
            else:
                main_df = pd.DataFrame([{k: d.get(k, None) for k in  direct_keys} for d in dics])

            # Merge with parent_df if it exists
            if parent_df is not None:
                main_df = parent_df.merge(main_df, left_on=parent_id_col, right_on=parent_id_col, how='left', suffixes=('', f'_{name}'))

            # Create the result dictionary
            res = {f'{sheet_number}_{name}' : main_df}
            sheet_number += 1
            # Recursive call for all sheet_keys
            for k in sheet_keys:
                lines = [_ for __ in dics for _ in __[k]]
                sub_sub_grid = sub_grid.get_field(k).object_type
                sheet_number, sheets = process(k, lines, main_df, my_id_column, sheet_number, sub_grid=sub_sub_grid)
                res = {**res, **sheets}
            return sheet_number, res
        
        sheets = process('document_level', dicts, parent_df = None, parent_id_col = None)[1]
        sheet_keys = list(sheets.keys())
        sorted_keys = grid.recursive_sheet_order()
        def ON(x):
            return '_'.join(x.split('_')[1:])
        sheet_keys.sort(key=
                        lambda x: sorted_keys.index(ON(x)) 
                        if ON(x) in sorted_keys 
                        else (
                            -1 if ON(x) == 'document_level'
                            else len(sorted_keys))
                        )
        sheets = {k: sheets[k] for k in sheet_keys}
        return XLSX(sheets=sheets)