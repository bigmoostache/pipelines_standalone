import pandas as pd
from typing import List
from custom_types.XLSX.type import XLSX

class Pipeline:
    def __init__(self):
        pass 

    def __call__(self, table : XLSX) -> List[str]:
        assert len(table.sheets) == 1, "Only one sheet is allowed"
        table = list(table.sheets.values())[0]
        return table.columns.tolist()