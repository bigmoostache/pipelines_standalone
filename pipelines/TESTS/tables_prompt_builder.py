import os
from typing import List

class Pipeline:
    def __init__(self, 
                 ):
        pass
        
    def __call__(self, dic : dict) -> str:
        return '{\n\t'+',\n\t'.join([f"\"{k}\" : {v['Type']} or null ({v['Description']})" for k,v in dic.items()])+'\n}'