from typing import List
from custom_types.XLSX.type import XLSX
import pandas as pd

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 dicts : List[dict]
                 ) -> XLSX:
        def process(name, dics : List[dict], parent_df = None, id_col = None):
            id_column = f'{name}_id'
            sheet_keys = list(set([k for dic in dics for k,v in dic.items() if isinstance(v, list)]))
            if len(sheet_keys) > 0:
                for i,d in enumerate(dics):
                    d[id_column] = i
                    for sheet in sheet_keys:
                        for _ in d[sheet]:
                            _[id_column] = i
            direct_keys = list(set([k for dic in dics for k,v in dic.items() if not isinstance(v, list)]))
            main_df = pd.DataFrame([{k:v for k,v in d.items() if k in direct_keys} for d in dics])
            if parent_df is not None:
                main_df = parent_df.merge(main_df, left_on=id_col, right_on=id_col, how='left', suffixes=('', f'_{name}'))
            res = {name : main_df}
            for k in sheet_keys:
                lines = [_ for __ in dics for _ in __[k]]
                sheets = process(k, lines, main_df, id_column)
                res = {**res, **sheets}
            return res
        return XLSX(sheets = process('Sheet1', dicts))