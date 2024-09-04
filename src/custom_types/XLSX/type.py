import pandas as pd, io

XLSX = pd.DataFrame

class Converter:
    extension = 'xlsx'
    @staticmethod
    def to_bytes(df: XLSX) -> bytes:
        output = io.BytesIO()
        df.to_excel(output, index=False)
        return output.getvalue()
    @staticmethod
    def from_bytes(b: bytes) -> XLSX:
        return pd.read_excel(b)
    @staticmethod
    def str_preview(df: XLSX) -> str:
        return df.to_string()
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='xlsx',
    _class = XLSX,
    converter = Converter,
    icon="/icons/xlsx.svg"
)