import pandas as pd
from typing import List

class Pipeline:
    def __init__(self):
        pass 
    def __call__(self, informations : List[dict]) -> pd.DataFrame:
        return pd.DataFrame(informations)