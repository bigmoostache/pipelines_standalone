from custom_types.JSONL.type import JSONL
from typing import List
import requests
import json



class Pipeline:

    ''' 
    If the requested key returns the value we wanted, we take it out in a new JSONL object
    '''

    def __init__(self, key : str, value : str):
        self.key = key
        self.value = value



    def __call__(self, jsonl : JSONL) -> JSONL:

        # loads the whole dataset as a python object
        data = [line for line in jsonl.lines]
        data_out = []
        try:
            for line in data:
                if line[self.key] == self.value:
                    data_out.append(line)
            return data_out

        except: 
            raise
        
