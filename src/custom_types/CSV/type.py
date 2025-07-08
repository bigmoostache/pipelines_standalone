import pandas as pd
import io
from typing import Dict

class CSV:
    def __init__(self, data: pd.DataFrame):
        self.data = data

class Converter:
    extension = 'csv'
   
    @staticmethod
    def to_bytes(df: CSV) -> bytes:
        output = io.StringIO()
        df.data.to_csv(output, index=False)
        return output.getvalue().encode('utf-8')
    
    @staticmethod
    def from_bytes(b: bytes) -> CSV:
        input_buffer = io.StringIO(b.decode('utf-8'))
        data = pd.read_csv(input_buffer)
        return CSV(data=data)
   
    @staticmethod
    def len(df: CSV) -> int:
        # total number of rows
        return len(df.data)

from custom_types.JSONL.type import JSONL

def convert_to_jsonl(df: CSV) -> JSONL:
    list_of_dicts = df.data.to_dict(orient='records')
    return JSONL(list_of_dicts)
   
from custom_types.wrapper import TYPE

wraped = TYPE(
    extension='csv',
    _class=CSV,
    converter=Converter,
    icon="/icons/csv.svg",
    additional_converters={
        'jsonl': convert_to_jsonl,
    },
    visualiser="https://vis.deepdocs.net/txt",
)