import pandas as pd
from custom_types.JSONL.type import JSONL
from custom_types.XLSX.type import XLSX

class Pipeline:
    def __init__(self):
        pass 
    def __call__(self, 
                 informations : JSONL,
                 initial_xlsx: XLSX
                 ) -> XLSX:
        assert len(initial_xlsx.sheets.keys()) == 1, "This pipeline only supports single-sheet XLSX files"
        key = list(initial_xlsx.sheets.keys())[0]
        return XLSX(sheets = {
            key: pd.DataFrame(informations.lines)
        })