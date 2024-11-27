import pandas as pd
from typing import List
from custom_types.JSONL.type import JSONL
from custom_types.XLSX.type import XLSX
class Pipeline:
    def __init__(self):
        pass 
    def __call__(self, informations : JSONL) -> XLSX:
        return XLSX(sheets = {
            "Sheet1": pd.DataFrame(informations.lines)
        })