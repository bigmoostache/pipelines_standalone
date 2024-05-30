import pandas as pd
from typing import List

class Pipeline:
    def __init__(self):
        pass 

    def __call__(self, table : pd.DataFrame) -> List[str]:
        return table.columns.tolist()