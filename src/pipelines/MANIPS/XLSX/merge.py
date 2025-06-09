from typing import List
from custom_types.XLSX.type import XLSX

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, data: List[XLSX]) -> XLSX:
        return XLSX(sheets={
            k:v for xlsx in data for k, v in xlsx.sheets.items()
        })