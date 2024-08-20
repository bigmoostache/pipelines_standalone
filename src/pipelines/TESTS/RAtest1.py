import os
from custom_types.RA.type import RA

class Pipeline:
    def __init__(self, 
                 param1 : str
                 ):
        self.param1 = param1
        
    def __call__(self, text_1 : str, text_2 : str) -> RA:
        return None
