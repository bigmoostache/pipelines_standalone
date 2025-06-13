from custom_types.XLSX.type import XLSX
import pandas as pd
import re

class Pipeline:
    def __init__(self):
        pass
   
    def __call__(self,
                columns: str,
                xlsx: XLSX
                ) -> XLSX:
        # Split columns on semicolons, commas, and line returns, then strip
        column_names = re.split(r'[;,\n]', columns)
        column_names = [name.strip() for name in column_names if name.strip()]
        
        if not column_names:
            raise ValueError("No valid column names provided")
        
        # Find each column in the sheets and validate
        column_locations = {}  # column_name -> (sheet_name, sheet_df)
        
        for column_name in column_names:
            found_in_sheets = []
            
            # Search for column in all sheets
            for sheet_name, sheet_df in xlsx.sheets.items():
                if column_name in sheet_df.columns:
                    found_in_sheets.append((sheet_name, sheet_df))
            
            # Validate column existence and uniqueness
            if len(found_in_sheets) == 0:
                raise ValueError(f"Column '{column_name}' not found in any sheet")
            elif len(found_in_sheets) > 1:
                sheet_names = [sheet[0] for sheet in found_in_sheets]
                raise ValueError(f"Column '{column_name}' found in multiple sheets: {sheet_names}")
            else:
                column_locations[column_name] = found_in_sheets[0]
        
        # Create new sheets with renamed columns
        new_sheets = {}
        for sheet_name, sheet_df in xlsx.sheets.items():
            new_df = sheet_df.copy()
            
            # Rename columns that need to be analyzed
            rename_dict = {}
            for column_name in column_names:
                if column_name in new_df.columns:
                    rename_dict[column_name] = f"analyze:{column_name}"
            
            if rename_dict:
                new_df = new_df.rename(columns=rename_dict)
            
            new_sheets[sheet_name] = new_df
        
        return XLSX(new_sheets)