import os, openai
from custom_types.XLSX.type import XLSX
from custom_types.XTRK.type import DataStructure, _create_model
import pandas as pd

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 xlsx : XLSX,
                 schema : DataStructure
                 ) -> dict:
        dic = {'grid': schema.model_dump_json()}
        df = pd.DataFrame(dic.items(), columns=['key', 'value'])
        xlsx.sheets['metadata'] = df
        return xlsx