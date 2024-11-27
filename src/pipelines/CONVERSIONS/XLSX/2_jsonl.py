from custom_types.JSONL.type import JSONL
from custom_types.XLSX.type import XLSX
import pandas as pd
class Pipeline:
    def __init__(self):
        pass

    def __call__(self, df : XLSX) -> JSONL:
        assert len(df.sheets) == 1, "Only one sheet is allowed"
        df = list(df.sheets.values())[0]
        list_of_dicts = df.to_dict(orient='records')
        return JSONL(list_of_dicts)