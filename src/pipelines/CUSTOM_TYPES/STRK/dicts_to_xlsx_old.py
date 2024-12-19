from typing import List
from custom_types.XLSX.type import XLSX
import pandas as pd

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 dicts : List[dict]
                 ) -> XLSX:
        def process(name, dics : List[dict], parent_df = None, id_col = None, sheet_number : int = 1):
            id_column = f'{name}_id'
            sheet_keys = list(set([k for dic in dics for k,v in dic.items() if isinstance(v, list)]))
            for i,d in enumerate(dics):
                d[id_column] = i
                for sheet in sheet_keys:
                    for _ in d[sheet]:
                        _[id_column] = i
            direct_keys = list(set([key for dic in dics for key,value in dic.items() if not isinstance(value, list)]))
            if parent_df is not None and id_col not in direct_keys:
                # Ensure the id_col is always present to avoid KeyError
                direct_keys.append(id_col)
            main_df = pd.DataFrame([{key:value for key,value in d.items() if key in direct_keys} for d in dics])
            if parent_df is not None:
                main_df = parent_df.merge(main_df, left_on=id_col, right_on=id_col, how='left', suffixes=('', f'_{name}'))
            res = {f'{sheet_number}_{name}' : main_df}
            sheet_number += 1
            for k in sheet_keys:
                lines = [_ for __ in dics for _ in __[k]]
                sheet_number, sheets = process(k, lines, main_df, id_column, sheet_number)
                res = {**res, **sheets}
            return sheet_number, res
        return XLSX(sheets = process('Sheet1', dicts)[1])