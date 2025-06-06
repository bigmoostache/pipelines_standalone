import pandas as pd
from typing import Dict, List
from custom_types.XLSX.type import XLSX
from pydantic import BaseModel, Field, create_model
from typing import Literal, Union
import re

class Parameter(BaseModel):
    name: str = Field(..., description="Name of the parameter")
    type: Literal['bool', 'float', 'int', 'categorical'] = Field(..., description="Type of the parameter. Can be 'bool', 'number', or 'categorical'")
    categories: List[str] = Field(default_factory=list, description="List of categories if type is categorical. Leave empty if not applicable")
    description: str = Field(..., description="Description of the parameter")
class Schema(BaseModel):
    parameters: List[Parameter] = Field(..., description="List of parameters in the schema")

    def create_dynamic_model(self, model_name):
        field_definitions = {}
        
        for param in self.parameters:
            if param.type == 'categorical':
                cats = list(set(param.categories + ['none']))
                field_type = (Literal[tuple(cats)], Field(..., description=param.description))
            elif param.type == 'bool':
                field_type = (Union[bool, None], Field(..., description=param.description))
            elif param.type == 'int':
                field_type = (Union[int, None], Field(..., description=param.description))
            elif param.type == 'float':
                field_type = (Union[float, None], Field(..., description=param.description))
            else:
                raise ValueError(f"Unknown type: {param.type}")
            
            # Ensure parameter name follows valid pattern (alphanumeric, underscore, hyphen)
            valid_param_name = re.sub(r'[^a-zA-Z0-9_-]', '_', param.name)
            field_definitions[valid_param_name] = (field_type[0], Field(..., description=param.description))
        valid_model_name = re.sub(r'[^a-zA-Z0-9_]', '_', model_name)
        return create_model(valid_model_name, **field_definitions)
        

def process_xlsx_pipeline(xlsx_input: XLSX) -> List[XLSX]:
    """
    Pipeline that processes an XLSX object and returns a list of XLSX objects.
   
    For each sheet in the input XLSX:
    - Keep ALL columns from the original dataframe
    - For each 'analyze:' column, create a new XLSX object containing:
      - All non-analyze columns (unchanged)
      - Only one 'analyze:' column (renamed to remove the 'analyze:' prefix)
   
    Args:
        xlsx_input (XLSX): Input XLSX object with sheets
       
    Returns:
        List[XLSX]: List of XLSX objects, one per analyze column per sheet
    """
    result_xlsx_list = []
   
    # Process each sheet in the input XLSX
    for sheet_name, df in xlsx_input.sheets.items():
        print(f"Processing sheet: {sheet_name}")
        # Get column names
        all_columns = df.columns.tolist()
        renames = {col:col.replace('analyze:', '').strip() for col in all_columns}
        df = df.rename(columns=renames)
        analyze_columns = [col for col in all_columns if col.startswith('analyze:')]

        # For each analyze column, create a new XLSX object
        for analyze_col in analyze_columns:
            # Create a copy of the dataframe to prevent side effects
            new_df = df.copy()
            result_xlsx_list.append(
                XLSX(sheets={analyze_col: new_df})
            )
   
    print(f"\nTotal XLSX objects created: {len(result_xlsx_list)}")
    return result_xlsx_list

class Pipeline:
    def __init__(self):
        pass
    
    def __call__(self, data: XLSX) -> List[XLSX]:
        return process_xlsx_pipeline(data)