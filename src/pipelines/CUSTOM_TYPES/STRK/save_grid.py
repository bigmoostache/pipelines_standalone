import os, openai
from custom_types.XLSX.type import XLSX
from custom_types.XTRK.type import DataStructure
import pandas as pd
import json

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 xlsx : XLSX,
                 schema : dict
                 ) -> XLSX:
        dic = {'grid': json.dumps(schema)}
        df = pd.DataFrame(dic.items(), columns=['key', 'value'])
        xlsx.sheets['metadata'] = df
        return xlsx