from custom_types.XLSX.type import XLSX
import pandas as pd
import json

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 xlsx : XLSX,
                 schema : dict
                 ) -> XLSX:
        xlsx.sheets['metadata'] = \
            pd.DataFrame(
                {'grid': json.dumps(schema)}.items(), 
                columns=['key', 'value']
                )
        return xlsx