from custom_types.JSONL.type import JSONL
import pandas as pd
class Pipeline:
    def __init__(self):
        pass

    def __call__(self, df : pd.DataFrame) -> JSONL:
        list_of_dicts = df.to_dict(orient='records')
        return JSONL(list_of_dicts)