import pandas as pd
from typing import List
from custom_types.JSONL.type import JSONL

class Pipeline:
    def __init__(self):
        pass 
    def __call__(self, informations : JSONL) -> pd.DataFrame:
        return pd.DataFrame(informations.lines)