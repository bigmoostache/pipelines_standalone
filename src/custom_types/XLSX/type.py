import pandas as pd, io
from typing import Dict

class XLSX:
    def __init__(self, sheets: Dict[str, pd.DataFrame]):
        self.sheets = sheets

class Converter:
    extension = 'xlsx'
    
    @staticmethod
    def to_bytes(df: XLSX) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for sheet_name, sheet_df in df.sheets.items():
                valid_sheet_name = sheet_name[:31]  # Truncate to 31 characters
                invalid_chars = [":", "\\", "/", "?", "*", "[", "]"]
                for char in invalid_chars:
                    valid_sheet_name = valid_sheet_name.replace(char, "_")  # Replace invalid chars with "_"
                if valid_sheet_name in writer.sheets:
                    raise ValueError(f"Duplicate sheet name detected: {valid_sheet_name}")

                sheet_df.to_excel(writer, sheet_name=valid_sheet_name, index=False)
        output.seek(0)  # Move the pointer to the start of the BytesIO buffer
        return output.getvalue()

    @staticmethod
    def from_bytes(b: bytes) -> XLSX:
        input_buffer = io.BytesIO(b)
        excel_file = pd.ExcelFile(input_buffer)
        sheets = {sheet_name: excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names}
        return XLSX(sheets=sheets)
    
    @staticmethod
    def len(df: XLSX) -> int:
        # total number of rows
        return sum([len(sheet) for sheet in df.sheets.values()])
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='xlsx',
    _class = XLSX,
    converter = Converter,
    icon="/icons/xlsx.svg"
    visualiser = "https://visualizations.croquo.com/xlsx",
)