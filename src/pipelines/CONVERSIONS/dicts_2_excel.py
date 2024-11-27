import pandas as pd
from custom_types.XLSX.type import XLSX
from typing import List

class Pipeline:
    def __init__(self):
        pass 
    def __call__(self, informations : List[dict]) -> XLSX:
        return XLSX(sheets = {
            "Sheet1": pd.DataFrame(informations)
        })