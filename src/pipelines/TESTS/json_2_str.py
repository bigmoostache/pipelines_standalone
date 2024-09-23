
from typing import Literal, List
from custom_types.JSON.type import JSON
import os

import json



class Pipeline:

    """
    
    This pipeline will take a JSON type and dump in int a string for handling of LLMs
    """

    def __init__(self, dummy_paramerter: str):
        
        self.dummy_paramerter = dummy_paramerter



    def __call__(self,  json_input : dict) -> str :
        json_string = json.dumps(json_input)
        return json_string
    
